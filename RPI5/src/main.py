#CentralWebSocket
import asyncio

import cv2
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from handlers import handle_move, handle_speed, handle_sensor
from state import rover_state
from visual.visuals_handler import visuals_handler
from queues import queues


app = FastAPI()

@app.websocket("/ws")
async def main(ws: WebSocket):
    await ws.accept()
    print('[ws] Client Connected')

    if not visuals_handler.initialize_camera():
        print("[ws] Failed to initialize camera, ur gonna have to do this without video, good luck :pray:")

    if not visuals_handler.initialize_human_detection():
        print("[ws] Failed to initialize human detection, running without human detection")

    # set rover up to send path update to ws send queue when the path updates
    async def send_path_update(data):
        await queues.send_queue.put(data)

    rover_state.on_path_update = send_path_update

    # initial path calculation
    rover_state.recalculate_path()

    # send current rover state
    await queues.send_queue.put({
        "type": "rover_status_data",
        "data": {
            "speed": rover_state.speed,
            "human_detection": visuals_handler.human_detection_enabled
        }
    })

    one = asyncio.create_task(recieve(ws))
    two = asyncio.create_task(send(ws))

    try:
        done, pending = await asyncio.wait(
            [one, two],
            return_when=asyncio.FIRST_COMPLETED
        )

        for task in pending:
            task.cancel()

        await asyncio.gather(*pending, return_exceptions=True)
        await asyncio.gather(*done, return_exceptions=True)

    except Exception as e:
        print(f'[ws] Error: {e}')
    finally:
        print('[ws] Cleaning up')


async def recieve(ws: WebSocket):
    try:
        while True:
            data = await ws.receive_json()
            print("[ws] Received Data: ", data) # uhm debugging lol

            match data["type"]:
                case "move_rover":
                    handle_move(data["data"])
                case "change_speed":
                    handle_speed(data["data"])
                case "enable_human_detection":
                    is_enabled = data["data"]["enable"]
                    if is_enabled:
                        visuals_handler.enable_human_detection()
                    else:
                        visuals_handler.disable_human_detection()

                # these dont do shit rn lol
                case "sensor":
                    handle_sensor(data)

    except WebSocketDisconnect:
        print('[ws] Receive task stopped')
        raise
    except Exception as e:
        print(f'[ws] Receive error: {e}')
        raise


async def send(ws: WebSocket):
    try:
        while True:
            try:
                camera_frame = queues.camera_queue.get_nowait()
                if visuals_handler.human_detection_enabled:
                    camera_frame = visuals_handler.run_human_detection(camera_frame)

                _, buffer = cv2.imencode('.jpg', camera_frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
                await ws.send_bytes(buffer.tobytes())
            except asyncio.QueueEmpty:
                pass

            # check queue for other stuff to send
            try:
                data = queues.send_queue.get_nowait()
                await ws.send_json(data)
                print("[ws] Sent Data: ", data)
            except asyncio.QueueEmpty:
                pass

            await asyncio.sleep(0.01)

    except asyncio.CancelledError:
        print('[ws] Send task cancelled')
        raise
    except WebSocketDisconnect:
        print('[ws] Send connection lost')
        raise
    except Exception as e:
        print(f'[ws] Send error: {e}')
        raise 
    finally:
        visuals_handler.cap.release()


# ------------ Jetbot stuff -------------------

@app.websocket("/jetbot")
async def jetbot_endpoint(ws: WebSocket):
    await ws.accept()
    print('[ws] JetBot Connected')

    one = asyncio.create_task(recieve_jetbot(ws))

    try:
        done, pending = await asyncio.wait(
            [one],
            return_when=asyncio.FIRST_COMPLETED
        )

        for task in pending:
            task.cancel()

        await asyncio.gather(*pending, return_exceptions=True)
        await asyncio.gather(*done, return_exceptions=True)

    except Exception as e:
        print(f'[ws] Error: {e}')
    finally:
        print('[ws] Cleaning up')


async def recieve_jetbot(ws: WebSocket):
    try:
        while True:
            data = await ws.receive()
            if type(data) == bytes:
                queues.camera_queue.put_nowait(data)

            match data["type"]:
               case "idk":
                   pass

    except WebSocketDisconnect:
        print('[ws] Receive task stopped')
        raise

    except Exception as e:
        print(f'[ws] Receive error: {e}')
        raise


async def send_jetbot(ws: WebSocket):
    try:
        while True:
            data = queues.jetbot_send_queue.get()
            await ws.send_json(data)

    except asyncio.CancelledError:
        print('[ws] Send task cancelled')
        raise
    except WebSocketDisconnect:
        print('[ws] Send connection lost')
        raise
    except Exception as e:
        print(f'[ws] Send error: {e}')
        raise