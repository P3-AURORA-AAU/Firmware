import asyncio
import websocket
import cv2
import numpy as np
import json

from ultralytics import YOLO

# Load the YOLO11 model
model = YOLO("./yolo11n_ncnn_model")

is_ready = True

WS_URI = "ws://localhost:8000/ws"
FRAME_TIMEOUT = 5
#------------------------------------------------------------
# Helper: convert raw bytes (e.g., JPEG) to an OpenCV image
# ----------------------------------------------------------------------
def bytes_to_cv_image(frame_bytes: bytes) -> np.ndarray:
    """Decode JPEG/PNG bytes into a BGR OpenCV image."""
    # Convert the byte buffer to a 1‑D NumPy array
    np_arr = np.frombuffer(frame_bytes, dtype=np.uint8)
    # Decode the image (cv2.IMREAD_COLOR returns BGR)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Failed to decode image – check payload format.")
    return img

# ----------------------------------------------------------------------
# Main coroutine – connects, grabs ONE frame, then closes
# ----------------------------------------------------------------------
async def fetch_one_frame() -> np.ndarray:
    async with websockets.connect(WS_URI) as ws:
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=FRAME_TIMEOUT)

            # msg arrives as a JSON string → parse it
            if isinstance(msg, str):
                data = json.loads(msg)

                if data.get("type") != "camera_data":
                    raise RuntimeError("Unexpected message type")

                b64img = data["data"]["image"]
                frame_bytes = base64.b64decode(b64img)

            else:
                raise RuntimeError("Expected JSON string from server")

            img = bytes_to_cv_image(frame_bytes)
            return img

        except asyncio.TimeoutError:
            raise RuntimeError(f"No frame received within {FRAME_TIMEOUT}s.")
# ----------------------------------------------------------------------
# Example usage – display the captured frame
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Run the async routine in the default event loop
    frame = asyncio.run(fetch_one_frame())

    # Simple OpenCV preview (press any key to close)
    cv2.imshow("Captured Frame", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    while True:

        # out, _ = (
        #     ffmpeg
        #     .input('/dev/video0', f='v4l2', input_format='mjpeg', video_size='1920x1080')
        #     .output('pipe:', vframes=1, format='image2', vcodec='mjpeg')
        #     .run(capture_stdout=True, capture_stderr=True)
        # )



        # Convert the bytes to a numpy array
        frame = cv2.imdecode(np.frombuffer(out, np.uint8), cv2.IMREAD_COLOR)

        # Run YOLO11 inference on the frame
        results = model(source=frame, imgsz=640)

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Display the resulting frame
        cv2.imwrite("photo.jpg", frame)


        # Break the loop if 'q' is pressed
        #if cv2.waitKey(1) == ord("q"):
        #    break

    # Release resources and close windows
    #cv2.destroyAllWindows()
