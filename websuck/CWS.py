#CentralWebSocket
import asyncio
import subprocess
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import cv2
import base64

app = FastAPI()

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
            try:
                await task
            except asyncio.CancelledError:
                pass

    except WebSocketDisconnect:
        print('[ws] Client disconnected')
    except Exception as e:
        print(f'[ws] Error: {e}')
    finally:
        print('[ws] Done doing stuff')

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
                # these dont do shit rn lol
                case "sensor":
                    sensor(data)
                case "stop":
                    stop(data) # this is just "none" in move data so remove this
    except WebSocketDisconnect:
        print('[ws] Receive task stopped')
        raise
    except Exception as e:
        print(f'[ws] Receive error: {e}')
        raise


async def send(ws: WebSocket):
    # waow cv2 instead so we dont have like 50 lines or something for image handling
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    try:
        while True:
            ret, frame = await asyncio.to_thread(cap.read)
            if not ret:
                break

            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
            jpeg_bytes = buffer.tobytes()

            await ws.send_bytes(jpeg_bytes)
    finally:
        cap.release()


# TODO: make ts actually do stuff
def handle_move(data):
    # "forward" | "backwards" | "left" | "right" | "forward_left" | "forward_right" | "backwards_left" | "backwards_right" | "none"
    print(f"Move: {data}")


def handle_speed(data):
    # "50%" | "100%"
    print(f"Speed: {data}")