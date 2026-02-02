import asyncio
import cv2
import websockets

CAMERA_DEVICE = "/dev/video0"
WS_HOST = "0.0.0.0"
WS_PORT = 8765
JPEG_QUALITY = 80  # 0–100

async def stream_camera(websocket):
    cap = cv2.VideoCapture(CAMERA_DEVICE)

    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")

    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Encode frame as JPEG
            success, jpg = cv2.imencode(".jpg", frame, encode_params)
            if not success:
                continue

            # Send as binary WebSocket message
            await websocket.send(jpg.tobytes())

            # Control FPS (~30)
            await asyncio.sleep(1 / 30)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        cap.release()

async def handler(websocket):
    await stream_camera(websocket)

async def main():
    print(f"WebSocket server listening on ws://{WS_HOST}:{WS_PORT}")
    async with websockets.serve(handler, WS_HOST, WS_PORT, max_size=None):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())

