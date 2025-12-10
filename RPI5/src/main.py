#CentralWebSocket
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import cv2
from handlers import handle_move, handle_speed, handle_sensor
from pathfinding.a_star import a_star_search
from state import rover_state
from visual.visuals_handler import visuals_handler

app = FastAPI()

send_queue = asyncio.Queue()

@app.websocket("/ws")
async def main(ws: WebSocket):
    await ws.accept()
    print('[ws] Client Connected')

    if not visuals_handler.initialize():
        print("[ws] Failed to initialize camera, ur gonna have to do this without video, good luck :pray:")

    # set rover up to send path update to ws send queue when the path updates
    async def send_path_update(data):
        await send_queue.put(data)

    rover_state.on_path_update = send_path_update

    # initial path calculation
    rover_state.recalculate_path()

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
                    # test thing, remove ts

                    await send_queue.put({
                        "type": "path_data",
                        "data": {
                            "grid": [
                                [0, 1, 0, 0, 1, 0, 0, 1, 0, 0],
                                [0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
                                [1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
                                [0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
                                [0, 1, 0, 0, 0, 0, 1, 0, 1, 0],
                                [0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
                                [1, 0, 0, 0, 0, 1, 0, 1, 0, 0],
                                [0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                                [0, 1, 0, 0, 0, 0, 1, 0, 1, 0],
                                [1, 0, 0, 1, 0, 1, 0, 0, 0, 0]
                            ],
                            "path": [[0, 0], [1, 0], [2, 0], [2, 1], [2, 2], [3, 2], [4, 2], [4, 3], [4, 4]],
                            "start": [0, 0],
                            "destination": [4, 4]
                        }
                    })

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
            if visuals_handler.camera_active:
                jpeg_bytes = await visuals_handler.generate_frame()
                if jpeg_bytes:
                    await ws.send_bytes(jpeg_bytes)

            # check queue for other stuff to send
            try:
                data = send_queue.get_nowait()
                await ws.send_json(data)
            except asyncio.QueueEmpty:
                pass

            await asyncio.sleep(0.01)
    except asyncio.CancelledError:
        print('[ws] Send task cancelled')
    finally:
        visuals_handler.cap.release()