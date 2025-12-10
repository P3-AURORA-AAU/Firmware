import asyncio

import cv2

class VisualsHandler:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.camera_active = True

        # check if camera actually opened
        if not self.cap.isOpened():
            print("[ws] ERROR: Cannot open camera!")
            self.camera_active = False
            return

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    # generate picture frame and return jpeg bytes
    async def generate_frame(self):
        # send image frame
        ret, frame = await asyncio.to_thread(self.cap.read)
        if not ret:
            return

        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
        return buffer.tobytes()

visuals_handler = VisualsHandler()