# visual/visuals_handler.py
import asyncio
import functools

import cv2
import numpy as np
from ultralytics import YOLO


async def to_thread_compat(func, /, *args, **kwargs):
    """
    Python 3.8-compatible replacement for asyncio.to_thread (added in 3.9).

    Runs `func(*args, **kwargs)` in the default thread pool executor and awaits the result.
    """
    loop = asyncio.get_running_loop()
    bound = functools.partial(func, *args, **kwargs)
    return await loop.run_in_executor(None, bound)


class VisualsHandler:
    def __init__(self):
        self.model = None
        self.human_detection_enabled = False

    # ----------------------------
    # Load YOLO model
    # ----------------------------
    def initialize_human_detection(self):
        """
        Load the YOLO model from disk.
        Returns True if successful, False otherwise.
        """
        try:
            self.model = YOLO("./visual/yolo11n_ncnn_model")
            print("[visuals] YOLO model loaded successfully")
            self.human_detection_enabled = False
            return True
        except Exception as e:
            print(f"[visuals] Failed to load YOLO model: {e}")
            self.model = None
            self.human_detection_enabled = False
            return False

    # ----------------------------
    # Enable / Disable human detection
    # ----------------------------
    def enable_human_detection(self):
        self.human_detection_enabled = True
        print("[visuals] Human detection enabled")

    def disable_human_detection(self):
        self.human_detection_enabled = False
        print("[visuals] Human detection disabled")

    # ----------------------------
    # Run YOLO detection on a single OpenCV frame
    # ----------------------------
    async def run_human_detection(self, frame):
        """
        Run YOLO on a single OpenCV frame asynchronously.
        Returns an annotated frame.
        """
        if self.model is None or not self.human_detection_enabled:
            return frame

        try:
            # Run YOLO in a separate thread to avoid blocking asyncio (Py3.8 compatible)
            results = await to_thread_compat(
                self.model,
                source=frame,
                imgsz=640,
                verbose=False,
            )
            annotated_frame = results[0].plot()
            return annotated_frame
        except Exception as e:
            print(f"[visuals] Human detection error: {e}")
            return frame

    # ----------------------------
    # Run YOLO on incoming JPEG bytes
    # ----------------------------
    async def run_human_detection_on_jpeg(self, jpeg_bytes):
        """
        Decode JPEG bytes, run human detection, and re-encode as JPEG bytes.
        Returns bytes ready to send over WebSocket.
        """
        try:
            np_arr = np.frombuffer(jpeg_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if frame is None:
                return None

            if self.human_detection_enabled:
                frame = await self.run_human_detection(frame)

            ok, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
            if not ok:
                return None
            return buffer.tobytes()
        except Exception as e:
            print(f"[visuals] Error processing JPEG: {e}")
            return None


# Instantiate a singleton for import
visuals_handler = VisualsHandler()

