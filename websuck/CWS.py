#CentralWebSocket
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import cv2

app = FastAPI()
send_queue = asyncio.Queue()

@app.websocket("/ws")
async def main(ws: WebSocket):
    await ws.accept()
    print('[ws] Client Connected')

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
                    sensor(data)

    except WebSocketDisconnect:
        print('[ws] Receive task stopped')
        raise
    except Exception as e:
        print(f'[ws] Receive error: {e}')
        raise


async def send(ws: WebSocket):
    # waow cv2 instead so we dont have like 50 lines or something for image handling
    cap = cv2.VideoCapture(0)

    # check if camera actually opened
    if not cap.isOpened():
        print("[ws] ERROR: Cannot open camera!")
        return


    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    try:
        while True:
            # send image frame
            ret, frame = await asyncio.to_thread(cap.read)
            if not ret:
                break

            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
            jpeg_bytes = buffer.tobytes()

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
        cap.release()


# TODO: make ts actually do stuff
def handle_move(data):
    # "forward" | "backwards" | "left" | "right" | "forward_left" | "forward_right" | "backwards_left" | "backwards_right" | "none"
    print(f"Move: {data}")


def handle_speed(data):
    # "50%" | "100%"
    print(f"Speed: {data}")