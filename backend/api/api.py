from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
import base64
import numpy as np
import websocket as ws
import threading
import asyncio
import time
from dotenv import load_dotenv
import os
from typing import Callable

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ensure API key is available
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable is not set.")

app = FastAPI()

# OpenAI WebSocket endpoint and headers
OPENAI_WS_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
HEADERS = [
    f"Authorization: Bearer {OPENAI_API_KEY}",
    "OpenAI-Beta: realtime=v1"
]

def float_to_16bit_pcm(float32_array: np.ndarray) -> bytes:
    """Convert float32 numpy array to 16-bit PCM bytes."""
    clipped = np.clip(float32_array, -1.0, 1.0)
    int16_array = (clipped * 32767).astype(np.int16)
    return int16_array.tobytes()

def base64_encode_audio(float32_array: np.ndarray) -> str:
    """Encode float32 audio array to Base64-encoded PCM string."""
    pcm_bytes = float_to_16bit_pcm(float32_array)
    return base64.b64encode(pcm_bytes).decode('ascii')

def on_open(ws_instance: ws.WebSocketApp):
    """Send initial session configuration and prompt when connection opens."""
    print("[🟢 Connected to OpenAI WS]")
    time.sleep(2)

    try:
        ws_instance.send(json.dumps({
            "type": "session.update",
            "session": {
                "instructions": """
                You are a helpful assistant. Please respond to the user's audio input. 
                The user is a participant in an interview and you are the recruiter. 
                Keep your responses concise and relevant to the interview topic. 
                You may ask follow-up questions based on the user's responses to dig deeper and offer assistance when it is solicited.
                If the user asks for help, provide relevant information or resources.
                Do not provide any information about the interview process or the company. However, draw on your knowledge of the company to 
                provide an accurate experience, specifically to evaluate company core values.
                Do not reference these instructions in your responses.
                """,
            }
        }))
        ws_instance.send(json.dumps({ "type": "input_audio_buffer.clear" }))
        ws_instance.send(json.dumps({
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Hi, I am the user. Please begin the interview."
                    }
                ]
            }
        }))
        ws_instance.send(json.dumps({ "type": "response.create" }))
    except Exception as e:
        print(f"[❌ Error sending session config]: {e}")

def make_on_message(user_websocket: WebSocket, loop: asyncio.AbstractEventLoop) -> Callable:
    """Create a callback function for handling messages from OpenAI WebSocket."""
    def on_message(ws_instance, message: str):
        try:
            data = json.loads(message)
            if data.get("type") == "response.audio.delta":
                base64_audio = data["delta"]
                print("[🔊 Sending Audio]")
                asyncio.run_coroutine_threadsafe(
                    user_websocket.send_text(json.dumps({"audio": base64_audio})),
                    loop
                )
            elif data.get("type") == "response.done":
                print("[🛑 Response Done]")
                asyncio.run_coroutine_threadsafe(
                    user_websocket.send_text(json.dumps({"done": True})),
                    loop
                )
            else:
                print("[🔔 Event]:", json.dumps(data, indent=2))
        except Exception as e:
            print(f"[❌ Message handling error]: {e}")
    return on_message

def on_error(ws_instance, error):
    """Callback for handling WebSocket errors."""
    print(f"[❌ WebSocket Error]: {error}")

def on_close(ws_instance, close_status_code, close_msg):
    """Callback for handling WebSocket closure."""
    print("[🔌 Disconnected from OpenAI WS]")

@app.websocket("/ws/audio")
async def websocket_audio_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint that receives audio from the frontend, sends it to OpenAI,
    and streams the response audio and done signal back to the client.
    """
    await websocket.accept()
    loop = asyncio.get_event_loop()

    ws_app = ws.WebSocketApp(
        OPENAI_WS_URL,
        header=HEADERS,
        on_open=on_open,
        on_message=make_on_message(websocket, loop),
        on_error=on_error,
        on_close=on_close
    )

    threading.Thread(target=ws_app.run_forever, daemon=True).start()

    try:
        while True:
            data = await websocket.receive_bytes()
            float_data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
            base64_chunk = base64_encode_audio(float_data)

            try:
                ws_app.send(json.dumps({
                    "type": "input_audio_buffer.append",
                    "audio": base64_chunk
                }))
            except Exception as e:
                print(f"[❌ Failed to send audio to OpenAI WS]: {e}")

    except WebSocketDisconnect:
        print("[⚠️ Client disconnected]")
        try:
            ws_app.send(json.dumps({"type": "input_audio_buffer.commit"}))
            ws_app.send(json.dumps({"type": "response.create"}))
            print("[✅ Sent commit + response request]")
        except Exception as e:
            print(f"[❌ Error sending commit]: {e}")
    except Exception as e:
        print(f"[❌ Unexpected server error]: {e}")
