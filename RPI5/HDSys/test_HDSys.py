from ultralytics import YOLO

# Load a YOLO11n PyTorch model
model = YOLO("./yolo11n_ncnn_model")

# Benchmark YOLO11n speed and accuracy on the COCO128 dataset for all all export formats
results = model(source="photo.jpg", imgsz=640)
