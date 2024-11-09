from ultralytics import YOLO

model = YOLO("/home/thanthien/Coding/bmd-v3.5/models/best_9_11.pt")

model.export(format="ncnn", imgsz=1080, name="thien_ncnn_model")