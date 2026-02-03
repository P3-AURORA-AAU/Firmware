import asyncio
import cv2
import websockets

CAMERA_DEVICE = "/dev/video0"
WS_HOST = "0.0.0.0"
WS_PORT = 8765
JPEG_QUALITY = 80
FPS = 30


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

            # Control FPS
            await asyncio.sleep(1.0 / FPS)

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        cap.release()


async def handler(websocket, path):
    # websockets on Python 3.6 typically uses (websocket, path)
    await stream_camera(websocket)


@asyncio.coroutine
def run_forever():
    # A "sleep forever" coroutine for 3.6
    while True:
        yield from asyncio.sleep(3600)


def main():
    print("WebSocket server listening on ws://{}:{}".format(WS_HOST, WS_PORT))

    loop = asyncio.get_event_loop()

    server_coro = websockets.serve(
        handler,
        WS_HOST,
        WS_PORT,
        max_size=None
    )

    server = loop.run_until_complete(server_coro)

    try:
        # Keep the loop alive
        loop.run_until_complete(run_forever())
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()


if __name__ == "__main__":
    main()