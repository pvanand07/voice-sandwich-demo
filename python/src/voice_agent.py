from typing import Any, Optional
import asyncio
from contextlib import suppress

from dotenv import load_dotenv
from typing_extensions import AsyncIterator
from langchain_core.runnables import RunnableGenerator
from langchain_core.messages import AIMessage
from langchain.agents import create_agent
import pyaudio

from assemblyai_stt import microphone_and_transcribe_once
from elevenlabs_tts import text_to_speech_stream

load_dotenv()


agent = create_agent(
    model="anthropic:claude-haiku-4-5",
    tools=[],
)


async def _stream_agent(
    input: AsyncIterator[tuple[AIMessage, Any]]
) -> AsyncIterator[str]:
    print("[DEBUG] _stream_agent: Starting agent stream")
    async for chunk in input:
        print(f"[DEBUG] _stream_agent: Received chunk: {chunk}")
        input_message = {"role": "user", "content": chunk}
        print(f"[DEBUG] _stream_agent: Sending to agent: {input_message}")
        async for message, _ in agent.astream({"messages": [input_message]}, stream_mode="messages"):
            print(f"[DEBUG] _stream_agent: Agent response: {message.text}")
            yield message.text


# ElevenLabs TTS - synthesize and play audio
async def _tts_stream(input: AsyncIterator[str]) -> AsyncIterator[str]:
    """
    Convert text to speech using ElevenLabs and play through speakers.

    Args:
        input: AsyncIterator of text strings from agent

    Yields:
        Status messages (for pipeline continuity)
    """
    print("[DEBUG] _tts_stream: Starting TTS")

    # Initialize audio output
    p = pyaudio.PyAudio()
    audio_stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        output=True,
        frames_per_buffer=1600
    )
    print("[DEBUG] Audio output stream opened")

    try:
        # Synthesize and play audio
        async for audio_chunk in text_to_speech_stream(input):
            # Play audio chunk through speakers
            await asyncio.get_event_loop().run_in_executor(
                None, audio_stream.write, audio_chunk
            )

        print("[DEBUG] _tts_stream: Finished playing audio")
        yield "tts_complete"

    finally:
        # Clean up audio
        audio_stream.stop_stream()
        audio_stream.close()
        p.terminate()
        print("[DEBUG] Audio output closed")


async def _run_agent_once(transcript: str) -> str:
    """Run the LCEL agent for a single user turn and return the response text."""
    if not transcript.strip():
        return ""

    print(f"\n[User]: {transcript}")
    print("[Agent]: ", end="", flush=True)

    agent_response_chunks: list[str] = []
    input_message = {"role": "user", "content": transcript}

    async for message, _ in agent.astream({"messages": [input_message]}, stream_mode="messages"):
        if hasattr(message, "text") and message.text:
            print(message.text, end="", flush=True)
            agent_response_chunks.append(message.text)

    print()  # newline after response
    return "".join(agent_response_chunks)


async def _play_tts_from_text(text: str, stop_event: Optional[asyncio.Event] = None) -> None:
    """Stream ElevenLabs audio and stop early if stop_event is set."""
    stripped = text.strip()
    if not stripped:
        print("[DEBUG] _play_tts_from_text: Empty response, skipping TTS")
        return

    async def agent_text_stream():
        yield stripped

    audio_generator = text_to_speech_stream(agent_text_stream())

    p = pyaudio.PyAudio()
    audio_stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        output=True,
        frames_per_buffer=1600,
    )

    loop = asyncio.get_event_loop()

    try:
        async for audio_chunk in audio_generator:
            if stop_event and stop_event.is_set():
                print("[DEBUG] _play_tts_from_text: Stop requested, ending playback early")
                break
            await loop.run_in_executor(None, audio_stream.write, audio_chunk)
        print("[DEBUG] _play_tts_from_text: Playback complete")
    except asyncio.CancelledError:
        print("[DEBUG] _play_tts_from_text: Cancelled while streaming audio")
        raise
    finally:
        with suppress(Exception):
            await audio_generator.aclose()
        audio_stream.stop_stream()
        audio_stream.close()
        p.terminate()


async def main():
    """
    Voice pipeline: Microphone → AssemblyAI STT → Agent → TTS

    Runs microphone capture concurrently with TTS playback so a fresh user turn
    can interrupt the current audio response as soon as AssemblyAI finalizes it.
    """
    print("Starting voice pipeline...")
    print("Speak into your microphone. Press Ctrl+C to stop.\n")

    turn_number = 0
    pending_transcript: Optional[str] = None
    pending_transcript_task: Optional[asyncio.Task[str]] = None

    try:
        while True:
            # Ensure we always have the next transcript ready to process
            if pending_transcript is None:
                if pending_transcript_task is None:
                    turn_number += 1
                    pending_transcript_task = asyncio.create_task(
                        microphone_and_transcribe_once(turn_number)
                    )
                transcript = await pending_transcript_task
                pending_transcript_task = None
            else:
                transcript = pending_transcript
                pending_transcript = None

            if not transcript:
                # No transcript captured, restart listening loop
                continue

            agent_response = await _run_agent_once(transcript)
            if not agent_response:
                continue

            stop_tts_event = asyncio.Event()
            tts_task = asyncio.create_task(
                _play_tts_from_text(agent_response, stop_event=stop_tts_event)
            )

            # Immediately start listening for the next user turn
            if pending_transcript_task is None:
                turn_number += 1
                pending_transcript_task = asyncio.create_task(
                    microphone_and_transcribe_once(turn_number)
                )

            # Race: either the user finishes speaking (new transcript) or TTS finishes
            wait_tasks = {tts_task}
            if pending_transcript_task:
                wait_tasks.add(pending_transcript_task)

            done, _ = await asyncio.wait(wait_tasks, return_when=asyncio.FIRST_COMPLETED)

            if pending_transcript_task and pending_transcript_task in done:
                try:
                    pending_transcript = pending_transcript_task.result()
                except Exception as mic_error:  # pragma: no cover - defensive logging
                    print(f"[DEBUG] main: Microphone task failed: {mic_error}")
                    pending_transcript = None
                pending_transcript_task = None
                stop_tts_event.set()
                await tts_task
            else:
                await tts_task
                if pending_transcript_task:
                    try:
                        pending_transcript = await pending_transcript_task
                    except Exception as mic_error:  # pragma: no cover
                        print(f"[DEBUG] main: Microphone task failed: {mic_error}")
                        pending_transcript = None
                    pending_transcript_task = None

    except KeyboardInterrupt:
        print("\n\nStopping pipeline...")
    except Exception as e:
        print(f"[DEBUG] main: Error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if pending_transcript_task:
            pending_transcript_task.cancel()
            with suppress(Exception):
                await pending_transcript_task


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
