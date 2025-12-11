"""
Test script for Hume TTS - saves audio to a file
"""

import asyncio
import wave
from pathlib import Path
from dotenv import load_dotenv
from hume_tts import HumeTTS

load_dotenv()


async def collect_audio(tts: HumeTTS, audio_data: bytearray):
    """Collect audio chunks from TTS events."""
    async for event in tts.receive_events():
        audio_data.extend(event.audio)
        print(f"Received {len(event.audio)} bytes")


async def test_hume_tts():
    """Test Hume TTS by generating audio and saving to file."""
    
    # Initialize Hume TTS
    tts = HumeTTS()
    
    # Text to synthesize
    test_text = "Hello, this is a test 22 of Hume AI text to speech."
    
    print(f"Synthesizing: {test_text}")
    
    # Collect audio chunks
    audio_data = bytearray()
    
    # Start receiving events in the background
    receive_task = asyncio.create_task(collect_audio(tts, audio_data))
    
    # Send text for synthesis
    await tts.send_text(test_text)
    
    # Wait a moment for audio to be generated
    await asyncio.sleep(3)
    
    # Close connection to end the stream
    await tts.close()
    
    # Wait for receive task to complete
    await receive_task
    
    # Save to WAV file
    output_file = Path("test_hume_output.wav")
    
    with wave.open(str(output_file), 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit = 2 bytes
        wav_file.setframerate(tts.sample_rate)
        wav_file.writeframes(audio_data)
    
    print(f"\nAudio saved to: {output_file}")
    print(f"Total size: {len(audio_data)} bytes")
    print(f"Sample rate: {tts.sample_rate} Hz")
    print(f"Format: WAV (16-bit PCM)")
    print(f"\nYou can now play the audio with any media player!")


if __name__ == "__main__":
    asyncio.run(test_hume_tts())

