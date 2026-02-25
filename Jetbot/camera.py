import asyncio
import cv2
import websockets

CAMERA_DEVICE = "/dev/video0"
WS_HOST = "0.0.0.0"
WS_PORT = 8765
JPEG_QUALITY = 80
FPS = 30


@asyncio.coroutine
def stream_camera(websocket):
    cap = cv2.VideoCapture(CAMERA_DEVICE)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam: {}".format(CAMERA_DEVICE))

    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), int(JPEG_QUALITY)]

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
            yield from websocket.send(jpg.tobytes())

            # Control FPS
            yield from asyncio.sleep(1.0 / float(FPS))

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        cap.release()


@asyncio.coroutine
def handler(websocket, path):
    # Python 3.6 websockets handler signature is (websocket, path)
    # 'path' is unused here but kept for compatibility.
    _ = path
    yield from stream_camera(websocket)


@asyncio.coroutine
def run_forever():
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
        loop.run_until_complete(run_forever())
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()


if __name__ == "__main__":
    main()
