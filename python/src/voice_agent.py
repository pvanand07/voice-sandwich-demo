from typing import Any

from dotenv import load_dotenv
from typing_extensions import AsyncIterator
from langchain_core.runnables import RunnableGenerator
from langchain_core.messages import AIMessage
from langchain.agents import create_agent

from assemblyai_stt import microphone_and_transcribe

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


# this is where we would call openai/11labs/etc. to generate text to speech
async def _tts_stream(input: str) -> AsyncIterator[str]:
    print(f"[DEBUG] _tts_stream: Got input: {input}")
    yield "hello"


audio_stream = (
    RunnableGenerator(microphone_and_transcribe)  # Combined mic + transcription
    | RunnableGenerator(_stream_agent)
    | RunnableGenerator(_tts_stream)
)


async def main():
    """
    Voice pipeline: Microphone → AssemblyAI STT → Agent → TTS
    """
    print("Starting voice pipeline...")
    print("Speak into your microphone. Press Ctrl+C to stop.\n")

    try:
        print("[DEBUG] main: Starting audio_stream.astream(None)")
        async for output in audio_stream.astream(None):
            print(f"[DEBUG] main: Final output: {output}")
    except KeyboardInterrupt:
        print("\n\nStopping pipeline...")
    except Exception as e:
        print(f"[DEBUG] main: Error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
