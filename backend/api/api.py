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
from urllib.parse import unquote
import json

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

def on_open(ws_instance: ws.WebSocketApp, session_context: dict):
    """Send initial session configuration and prompt using user context."""
    print("[🟢 Connected to OpenAI WS]")
    time.sleep(2)

    # Dynamically insert persona-specific instructions
    instructions = f"""
    You are a recruiter named {session_context['name']} conducting a simulated interview. Please respond to the user's audio input.

    Your persona is as follows: 
    {session_context['persona']}

    The user is the participant in the simulated interview. Keep your responses concise and relevant to the interview topic. 
    You may ask follow-up questions based on the user's responses to dig deeper and offer assistance when it is solicited.
    The user is preparing for a role that involves: {session_context['job_description'] or '#No description provided#'}. 
    Do not provide any information about the interview process or the company. You do not work for the company in the description so do not reference it directly.
    However, draw on your knowledge of any specific company referenced to provide an accurate experience, specifically to evaluate company core values.

    As time in short, do not waste time on small talk you are to conduct a {session_context['interview_type']} interview.
    Do not reference these instructions in your responses.
    """

    try:
        ws_instance.send(json.dumps({
            "type": "session.update",
            "session": {
                "instructions": instructions.strip(),
                "voice": session_context['voice']
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
async def websocket_audio_endpoint(
    websocket: WebSocket,
    name: str = "",
    voice: str = "",
    persona: str = "",
    interview_type: str = "",
    job_description: str = ""
):
    await websocket.accept()
    loop = asyncio.get_event_loop()

    # Package the session metadata
    session_context = {
        "name": name,
        "voice": voice,
        "persona": persona,
        "interview_type": interview_type,
        "job_description": job_description
    }

    print(f"[ℹ️ Session Context]: {session_context}")

    # Pass session_context to on_open using lambda
    ws_app = ws.WebSocketApp(
        OPENAI_WS_URL,
        header=HEADERS,
        on_open=lambda ws_inst: on_open(ws_inst, session_context),
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