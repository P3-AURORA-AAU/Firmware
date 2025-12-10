import cv2
from fastapi import FastAPI, WebSocket
import base64
import time

app = FastAPI()

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
if not cap.isOpened():
    raise RuntimeError("Unable to open video device")

# Force format & framerate
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FPS, 30.000)

@app.get("/")
async def read_main():
    return {"msg": "Hello World"}


@app.websocket("/ws")
async def websocket(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"msg": "Hello WebSocket"})
    await websocket.close()


@app.websocket("/camera")
async def producer(websocket: WebSocket):
    await websocket.accept()
    """Grab frames from the camera, encode, and broadcast."""
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Encode as JPEG (fast, low latency)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
        success, jpg_buf = cv2.imencode('.jpg', frame, encode_param)
        if not success:
            continue

        # Convert to bytes for transmission
        data = jpg_buf.tobytes()

        await websocket.send_json({"data" : base64.b64encode(data.encode("utf-8"))})

        # Sleep to roughly match target FPS
        await time.sleep(1 / 30)
    await websocket.close()
