# main.py
# CentralWebSocket (headless YOLO client with IMU and movement POST)
import asyncio
from functools import partial

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from handlers import handle_move, handle_sensor
from state import rover_state
from visual.visuals_handler import visuals_handler
from queues import queues

import websockets
import requests

# ----------------------------
# Configuration
# ----------------------------
CAMERA_WS_URL = "ws://10.42.7.85:8765"  # Camera WebSocket stream
IMU_URL = "http://10.42.7.85:5000/imu/collect"  # IMU endpoint (your code uses POST)
MOVEMENT_URL = "http://10.42.7.85:5000/move"  # POST movement

MOVE_ACTIONS = {
    "stop": "stop",
    "forward": "forward",
    "backward": "backward",
    "left": "left",
    "right": "right",
    "moving_left": "moving_left",
    "moving_right": "moving_right",
}

app = FastAPI()

# ----------------------------
# asyncio.to_thread compatibility for Python < 3.9
# ----------------------------
async def to_thread_compat(func, /, *args, **kwargs):
    """
    Replacement for asyncio.to_thread (Python 3.9+).
    Runs a blocking function in the default threadpool executor.
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(func, *args, **kwargs))


# ----------------------------
# Camera WS client
# ----------------------------
async def camera_ws_client():
    while True:
        try:
            async with websockets.connect(CAMERA_WS_URL, max_size=None) as ws:
                print(f"[camera_ws] Connected to {CAMERA_WS_URL}")
                async for message in ws:
                    if isinstance(message, (bytes, bytearray)):
                        queues.camera_queue.put_nowait(message)
        except Exception as e:
            print(f"[camera_ws] Connection error: {e}")
            await asyncio.sleep(1)  # backoff then reconnect


# ----------------------------
# IMU polling (POST)
# ----------------------------
def fetch_imu_data_blocking():
    try:
        response = requests.post(IMU_URL, timeout=1)  # your external endpoint is POST
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[IMU] POST failed: {e}")
        return None


async def imu_polling_loop():
    while True:
        imu_data = await to_thread_compat(fetch_imu_data_blocking)
        if imu_data:
            rover_state.process_imu_data(imu_data)
        await asyncio.sleep(0.1)  # poll every 100ms


# ----------------------------
# Startup: create background tasks safely (DON'T create tasks at import time)
# ----------------------------
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(camera_ws_client())
    asyncio.create_task(imu_polling_loop())


# ----------------------------
# Movement POST function
# ----------------------------
def send_movement_command_blocking(action: str):
    if action not in MOVE_ACTIONS:
        print(f"[Movement] Invalid action: {action}")
        return

    url = f"{MOVEMENT_URL}/{action}"  # POST /move/<action>
    try:
        response = requests.post(url, timeout=1)
        response.raise_for_status()
        print(f"[Movement] Sent action '{action}', response: {response.text}")
    except Exception as e:
        print(f"[Movement] Failed to send action '{action}': {e}")


async def send_movement_command(action: str):
    await to_thread_compat(send_movement_command_blocking, action)


# ----------------------------
# Main WebSocket endpoint
# ----------------------------
@app.websocket("/ws")
async def main(ws: WebSocket):
    await ws.accept()
    print("[ws] Client Connected")

    if not visuals_handler.initialize_human_detection():
        print("[ws] Failed to initialize human detection, running without human detection")

    # Setup rover path update callback
    async def send_path_update(data):
        await queues.send_queue.put(data)

    rover_state.on_path_update = send_path_update
    rover_state.recalculate_path()

    # Send initial rover status
    await queues.send_queue.put(
        {
            "type": "rover_status_data",
            "data": {
                "speed": rover_state.speed,
                "human_detection": visuals_handler.human_detection_enabled,
            },
        }
    )

    one = asyncio.create_task(recieve(ws))
    two = asyncio.create_task(send(ws))

    try:
        done, pending = await asyncio.wait([one, two], return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
        await asyncio.gather(*done, return_exceptions=True)

    except Exception as e:
        print(f"[ws] Error: {e}")
    finally:
        print("[ws] Cleaning up")


# ----------------------------
# Receive JSON commands from client
# ----------------------------
async def recieve(ws: WebSocket):
    try:
        while True:
            data = await ws.receive_json()
            print("[ws] Received Data: ", data)  # uhm debugging lol

            msg_type = data.get("type")

            if msg_type == "move_rover":
                handle_move(data.get("data"))

            elif msg_type == "change_speed":
                # NOTE: handle_speed is referenced in your original code but not imported/defined here.
                # Leaving as-is so you can wire it up in your project.
                handle_speed(data.get("data"))

            elif msg_type == "enable_human_detection":
                payload = data.get("data", {})
                is_enabled = payload.get("enable", False)

                if is_enabled:
                    visuals_handler.enable_human_detection()
                else:
                    visuals_handler.disable_human_detection()

            # these dont do shit rn lol
            elif msg_type == "sensor":
                handle_sensor(data)

            else:
                print(f"[ws] Unknown message type: {msg_type}")

    except WebSocketDisconnect:
        print("[ws] Receive connection lost")
        raise
    except asyncio.CancelledError:
        print("[ws] Receive task cancelled")
        raise
    except Exception as e:
        print(f"[ws] Receive error: {e}")
        raise


# ----------------------------
# Send frames and rover data to client
# ----------------------------
async def send(ws: WebSocket):
    try:
        while True:
            # Camera frames
            try:
                jpeg_bytes = queues.camera_queue.get_nowait()
                if visuals_handler.human_detection_enabled:
                    jpeg_bytes = await visuals_handler.run_human_detection_on_jpeg(jpeg_bytes)
                await ws.send_bytes(jpeg_bytes)
            except asyncio.QueueEmpty:
                pass

            # Other queued data
            try:
                data = queues.send_queue.get_nowait()
                await ws.send_json(data)
                print("[ws] Sent Data:", data)
            except asyncio.QueueEmpty:
                pass

            await asyncio.sleep(0.01)

    except asyncio.CancelledError:
        print("[ws] Send task cancelled")
        raise
    except WebSocketDisconnect:
        print("[ws] Send connection lost")
        raise
    except Exception as e:
        print(f"[ws] Send error: {e}")
        raise

