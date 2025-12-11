"""
Hume AI Text-to-Speech Streaming

Python implementation of Hume's streaming TTS API using WebSocket.
Converts text to PCM audio in real-time using WebSocket streaming.

Input: Text strings
Output: TTS events (tts_chunk for audio chunks)
"""

import asyncio
import base64
import contextlib
import json
import os
from typing import AsyncIterator, Literal, Optional

import websockets
from websockets.client import WebSocketClientProtocol

from events import TTSChunkEvent


class HumeTTS:
    _ws: Optional[WebSocketClientProtocol]
    _connection_signal: asyncio.Event
    _close_signal: asyncio.Event

    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_name: str = "Male English Actor",
        voice_provider: Literal["HUME_AI", "CUSTOM_VOICE"] = "HUME_AI",
        model_version: Literal["1", "2"] = "1",
        sample_rate: int = 48000,
        audio_format: Literal["pcm", "mp3", "wav"] = "pcm",
        instant_mode: bool = True,
        strip_headers: bool = True,
        description: Optional[str] = None,
        speed: Optional[float] = None,
        trailing_silence: Optional[float] = None,
    ):
        self.api_key = api_key or os.getenv("HUME_API_KEY")
        if not self.api_key:
            raise ValueError("Hume API key is required")

        self.voice_name = voice_name
        self.voice_provider = voice_provider
        self.model_version = model_version
        self.sample_rate = sample_rate
        self.audio_format = audio_format
        self.instant_mode = instant_mode
        self.strip_headers = strip_headers
        self.description = description
        self.speed = speed
        self.trailing_silence = trailing_silence
        self._ws = None
        self._connection_signal = asyncio.Event()
        self._close_signal = asyncio.Event()
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._message_handler_task: Optional[asyncio.Task] = None

    async def send_text(self, text: Optional[str]) -> None:
        if text is None:
            return

        if not text.strip():
            return

        ws = await self._ensure_connection()

        # Build the utterance payload
        utterance = {
            "text": text,
            "voice": {
                "name": self.voice_name,
                "provider": self.voice_provider,
            },
        }

        # Add optional parameters
        if self.description:
            utterance["description"] = self.description
        if self.speed is not None:
            utterance["speed"] = self.speed
        if self.trailing_silence is not None:
            utterance["trailing_silence"] = self.trailing_silence

        await ws.send(json.dumps(utterance))
        
        # Send flush message to trigger immediate generation
        await ws.send(json.dumps({"flush": True}))

    async def receive_events(self) -> AsyncIterator[TTSChunkEvent]:
        while not self._close_signal.is_set():
            _, pending = await asyncio.wait(
                [
                    asyncio.create_task(self._close_signal.wait()),
                    asyncio.create_task(self._connection_signal.wait()),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            with contextlib.suppress(asyncio.CancelledError):
                for task in pending:
                    task.cancel()

            if self._close_signal.is_set():
                break

            if self._connection_signal.is_set():
                self._connection_signal.clear()
                try:
                    # Read from the message queue populated by the background handler
                    while not self._close_signal.is_set():
                        try:
                            # Wait for messages with a timeout to check close signal periodically
                            message = await asyncio.wait_for(
                                self._message_queue.get(), timeout=0.1
                            )
                            
                            if message is None:
                                # None signals end of stream
                                break
                            
                            yield message
                            
                        except asyncio.TimeoutError:
                            continue
                        
                except Exception as e:
                    print(f"[DEBUG] Hume receive error: {e}")
                finally:
                    # Clean up on exit
                    if self._ws and self._ws.close_code is None:
                        await self._ws.close()
                    self._ws = None

    async def _message_handler(self):
        """
        Background task that receives WebSocket messages and queues audio chunks.
        This runs concurrently with receive_events() to handle incoming messages.
        """
        try:
            if not self._ws:
                return

            async for raw_message in self._ws:
                try:
                    message = json.loads(raw_message)
                    
                    # Check for errors
                    if message.get("type") == "error":
                        print(f"[DEBUG] Hume error: {message}")
                        await self._message_queue.put(None)
                        break
                    
                    # Extract and decode audio
                    audio_b64 = message.get("audio")
                    if audio_b64:
                        audio_chunk = base64.b64decode(audio_b64)
                        if audio_chunk:
                            await self._message_queue.put(TTSChunkEvent.create(audio_chunk))
                    
                    # Check if this is the end of the response
                    # Hume doesn't send explicit "done" but we can check for completion
                    
                except json.JSONDecodeError as e:
                    print(f"[DEBUG] Hume JSON decode error: {e}")
                    continue
                    
        except websockets.exceptions.ConnectionClosed:
            print("Hume: WebSocket connection closed")
        except Exception as e:
            print(f"[DEBUG] Hume message handler error: {e}")
        finally:
            # Signal end of stream
            await self._message_queue.put(None)

    async def close(self) -> None:
        # Send close message before closing the WebSocket
        if self._ws and self._ws.close_code is None:
            try:
                await self._ws.send(json.dumps({"close": True}))
            except Exception:
                pass
            await self._ws.close()
        
        self._ws = None
        self._close_signal.set()
        
        # Cancel message handler task
        if self._message_handler_task and not self._message_handler_task.done():
            self._message_handler_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._message_handler_task

    async def _ensure_connection(self) -> WebSocketClientProtocol:
        if self._close_signal.is_set():
            raise RuntimeError(
                "HumeTTS tried establishing a connection after it was closed"
            )
        if self._ws and self._ws.close_code is None:
            return self._ws

        # Build WebSocket URL with query parameters
        params = [
            f"api_key={self.api_key}",
            f"instant_mode={'true' if self.instant_mode else 'false'}",
            f"strip_headers={'true' if self.strip_headers else 'false'}",
            "no_binary=true",  # Request JSON responses instead of binary
        ]
        url = f"wss://api.hume.ai/v0/tts/stream/input?{'&'.join(params)}"
        
        self._ws = await websockets.connect(url)
        
        # Start the background message handler
        self._message_handler_task = asyncio.create_task(self._message_handler())
        
        self._connection_signal.set()
        return self._ws

