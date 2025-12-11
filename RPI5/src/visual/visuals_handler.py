import asyncio
from ultralytics import YOLO
import cv2

class VisualsHandler:
    def __init__(self):
        self.cap = None
        self.camera_active = True
        self.model = None
        self.human_detection_enabled = False

    def initialize_camera(self):
        # if cap already exists... no it doesnt
        if self.cap is not None:
            self.cap.release()
            self.cap = None

        try:
            self.cap = cv2.VideoCapture(0)

            # check if camera actually opened
            if not self.cap.isOpened():
                print("[ws] ERROR: Cannot open camera!")
                self.camera_active = False
                return False

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.camera_active = True

            return True

        except Exception as e:
            print(f"[ws] Camera initialization error: {e}")
            self.camera_active = False
            return False

    def initialize_human_detection(self):
        try:
            self.model = YOLO("./visual/yolo11n_ncnn_model")
            print("[ws] YOLO model loaded successfully")
            return True
        except Exception as e:
            print(f"[ws] YOLO model loading error: {e}")
            return False

    def enable_human_detection(self):
        self.human_detection_enabled = True
        print("[ws] Human detection enabled")

    def disable_human_detection(self):
        self.human_detection_enabled = False
        print("[ws] Human detection disabled")

    async def run_human_detection(self, frame):
        try:
            results = await asyncio.to_thread(
                self.model,
                source=frame,
                imgsz=640,
                verbose=False, # unless u want a million logs about inference
            )

            annotated_frame = results[0].plot()
            return annotated_frame

        except Exception as e:
            print(f"[ws] Human detection error: {e}")
            return None

    # releasing the camera might be a good idea actually
    def release_camera(self):
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception as e:
                print(f"[ws] Camera release error: {e}")
            finally:
                self.cap = None
                self.camera_active = False

    # generate picture frame and return jpeg bytes
    async def generate_frame(self):
        # error handling??? what is this dark sorcery
        if not self.camera_active or self.cap is None:
            return None

        ret, frame = await asyncio.to_thread(self.cap.read)
        if not ret:
            return None

        # if enabled, do detection
        if self.human_detection_enabled:
            frame = await self.run_human_detection(frame)

        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
        return buffer.tobytes()

visuals_handler = VisualsHandler()