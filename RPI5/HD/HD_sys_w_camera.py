import cv2
import ffmpeg
import numpy as np

from ultralytics import YOLO

# Load the YOLO11 model
model = YOLO("./yolo11n_ncnn_model")

while True:
    out, _ = (
        ffmpeg
        .input('/dev/video0', f='v4l2', input_format='mjpeg', video_size='1920x1080')
        .output('pipe:', vframes=1, format='image2', vcodec='mjpeg')
        .run(capture_stdout=True, capture_stderr=True)
    )

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
