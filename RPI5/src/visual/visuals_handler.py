import asyncio

import cv2

class VisualsHandler:
    def __init__(self):
        self.cap = None
        self.camera_active = True

    def initialize(self):
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

    # releasing the camera might be a good idea actually
    def release_camera(self):
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception as e:
                print(f"[ws] Camera release error: {e}")
            finally:
                self.cap = None
                camera_active = False

    # generate picture frame and return jpeg bytes
    async def generate_frame(self):
        # error handling??? what is this dark sorcery
        if not self.camera_active or self.cap is None:
            return None

        ret, frame = await asyncio.to_thread(self.cap.read)
        if not ret:
            return None

        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
        return buffer.tobytes()

visuals_handler = VisualsHandler()