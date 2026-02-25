# main.py
# CentralWebSocket (headless YOLO client with IMU and movement POST)
import asyncio
from functools import partial

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from state import RoverState, send_movement_command_blocking
from visual.visuals_handler import visuals_handler
from queues import queues
import websockets
import requests

# Optional: your handlers
from handlers import handle_move, handle_sensor  # your existing handlers

# ----------------------------
# Configuration
# ----------------------------
CAMERA_WS_URL = "ws://10.42.7.85:8765"
IMU_URL = "http://10.42.7.85:5000/imu/collect"

app = FastAPI()


# ----------------------------
# Async wrapper for blocking functions
# ----------------------------
async def to_thread_compat(func, /, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(func, *args, **kwargs))


# ----------------------------
# Camera WebSocket client
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
            await asyncio.sleep(1)


# ----------------------------
# IMU polling
# ----------------------------
def fetch_imu_data_blocking():
    try:
        response = requests.post(IMU_URL, timeout=1)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[IMU] POST failed: {e}")
        return None


async def imu_polling_loop():
    while True:
        imu_data = await to_thread_compat(fetch_imu_data_blocking)
        if imu_data and hasattr(RoverState, "process_imu_data"):
            RoverState.process_imu_data(imu_data)
        await asyncio.sleep(0.2)


# ----------------------------
# Async wrapper for rover movement
# ----------------------------
async def send_drive_cmd(cmd):
    """
    Sends movement commands to the robot using your POST endpoint.
    """
    await to_thread_compat(send_movement_command_blocking, cmd)




# ----------------------------
# WebSocket endpoint
# ----------------------------
@app.websocket("/ws")
async def main(ws: WebSocket):
    await ws.accept()
    print("[ws] Client Connected")

    # Initialize human detection
    if not visuals_handler.initialize_human_detection():
        print("[ws] Failed to initialize human detection")

    # Hook rover callbacks
    RoverState.on_drive_cmd = send_drive_cmd
    RoverState.on_path_update = send_path_to_fe
    
    RoverState.recalculate_path()
    

    # Send initial rover status
    await queues.send_queue.put({
        "type": "rover_status_data",
        "data": {
            "speed": getattr(RoverState, "speed", 0),
            "human_detection": visuals_handler.human_detection_enabled,
        },
    })

    receive_task = asyncio.create_task(receive(ws))
    send_task = asyncio.create_task(send(ws))

    try:
        done, pending = await asyncio.wait(
            [receive_task, send_task], return_when=asyncio.FIRST_COMPLETED
        )
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
async def receive(ws: WebSocket):
    try:
        while True:
            data = await ws.receive_json()
            print("[ws] Received Data:", data)

            msg_type = data.get("type")

            if msg_type == "move_rover":
                handle_move(data.get("data"))

            elif msg_type == "change_speed":
                if "handle_speed" in globals():
                    handle_speed(data.get("data"))

            elif msg_type == "enable_human_detection":
                payload = data.get("data", {})
                if payload.get("enable", False):
                    visuals_handler.enable_human_detection()
                else:
                    visuals_handler.disable_human_detection()

            elif msg_type == "sensor":
                handle_sensor(data)
            
            elif msg_type == "enable_autonomous_driving":
                payload = data.get("data", {})
                enable = payload.get("enable", False)

                if enable:
                    print("[ws] Autonomous driving ENABLED")
                    RoverState.recalculate_path()
                    RoverState.start_autonomous()
                else:
                    print("[ws] Autonomous driving DISABLED")
                    RoverState.stop_autonomous()


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
async def send_path_to_fe(data):
    msg = {"type": "path_data", "data": data}
    queues.send_queue.put_nowait(msg)


async def send(ws: WebSocket):
    try:
        while True:
            # ---- Camera frames ----
            jpeg_bytes = None
            while not queues.camera_queue.empty():
                jpeg_bytes = queues.camera_queue.get_nowait()

            if jpeg_bytes is not None:
                if visuals_handler.human_detection_enabled:
                    jpeg_bytes = await visuals_handler.run_human_detection_on_jpeg(jpeg_bytes)
                await ws.send_bytes(jpeg_bytes)

            # ---- Other queued data ----
            # Send ALL pending JSON messages this tick
            while not queues.send_queue.empty():
                data = queues.send_queue.get_nowait()
                try:
                    await ws.send_json(data)
                    print(f"[ws] sent JSON type={data.get('type')}")
                except Exception as e:
                    print(f"[ws] failed sending JSON ({data.get('type')}): {e}")

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

# ----------------------------
# Startup tasks
# ----------------------------
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(camera_ws_client())

