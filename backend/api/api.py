from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import wave
import os
from datetime import datetime
import json
import base64
import numpy as np
import sounddevice as sd
import websocket as ws
import threading
import asyncio

app = FastAPI()

OPENAI_API_KEY = ""
url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
headers = [
    "Authorization: Bearer " + OPENAI_API_KEY,
    "OpenAI-Beta: realtime=v1"
]

# PCM Conversion Helper
def float_to_16bit_pcm(float32_array):
    clipped = np.clip(float32_array, -1.0, 1.0)
    int16_array = (clipped * 32767).astype(np.int16)
    return int16_array.tobytes()

def base64_encode_audio(float32_array):
    pcm_bytes = float_to_16bit_pcm(float32_array)
    return base64.b64encode(pcm_bytes).decode('ascii')

# WebSocket callbacks for OpenAI API
def on_open(ws):
    print("[🟢 Connected]")
    ws.send(json.dumps({
        "type": "session.update",
        "session": {
            "instructions": "Never use the word 'moist' in your responses!"
        }
    }))
    ws.send(json.dumps({ "type": "input_audio_buffer.clear" }))

# def on_message(ws, message):
#     data = json.loads(message)
#     if data.get("type") == "response.audio.delta":
#         base64_audio = data["delta"]
#         pcm_bytes = base64.b64decode(base64_audio)
#         audio_array = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
#         sd.play(audio_array, samplerate=24000)
#         sd.wait()
#     elif data.get("type") == "response.done":
#         print("\n[🛑 Response Done]")
#     else:
#         print("🔔 Event:", json.dumps(data, indent=2))


def on_message(ws, message):
    data = json.loads(message)

    if data.get("type") == "response.audio.delta":
        base64_audio = data["delta"]

        # Send to browser WebSocket
        if ws:
            # Wrap in asyncio task to run in background
            asyncio.create_task(
                ws.send(json.dumps({
                "audio": base64_audio
            }))
            )
            
    elif data.get("type") == "response.done":
        print("\n[🛑 Response Done]")
        if ws:
            asyncio.create_task(ws.send(json.dumps({"done": True})))
    else:
        print("🔔 Event:", json.dumps(data, indent=2))

def on_error(ws, error):
    print("❌ Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("🔌 Disconnected")

# FastAPI WebSocket endpoint
@app.websocket("/ws/audio")
async def websocket_audio_endpoint(websocket: WebSocket):
    await websocket.accept()

    batch_index = 0
    writer = None

    # Initialize OpenAI WebSocket client
    ws_app = ws.WebSocketApp(
        url,
        header=headers,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    threading.Thread(target=ws_app.run_forever, daemon=True).start()

    try:
        while True:
            # Receive audio data from the client
            data = await websocket.receive_bytes()

            # Convert audio data to float32 format
            float_data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0

            # Encode audio data to Base64
            base64_chunk = base64_encode_audio(float_data)

            # Send audio data directly to OpenAI WebSocket
            ws_app.send(json.dumps({
                "type": "input_audio_buffer.append",
                "audio": base64_chunk
            }))

    except WebSocketDisconnect:
        if writer:
            writer.close()
            print(f"Saved final batch {batch_index}")
        ws_app.send(json.dumps({ "type": "input_audio_buffer.commit" }))
        ws_app.send(json.dumps({ "type": "response.create" }))
        print("[✅ Sent commit + response request]")
    except Exception as e:
        if writer:
            writer.close()
        print(f"Error: {e}")
        raise e