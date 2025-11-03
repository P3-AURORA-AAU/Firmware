import ffmpeg
import numpy as np
import cv2

out, _ = (
    ffmpeg
    .input('/dev/video0', f='v4l2', input_format='mjpeg', video_size='1920x1080')
    .output('pipe:', vframes=1, format='image2', vcodec='mjpeg')
    .run(capture_stdout=True, capture_stderr=True)
)

# Convert the bytes to a numpy array
frame = cv2.imdecode(np.frombuffer(out, np.uint8), cv2.IMREAD_COLOR)

cv2.imwrite("photo.jpg", frame)
cv2.waitKey(0)
