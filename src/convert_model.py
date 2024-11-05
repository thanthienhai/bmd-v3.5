from ultralytics import YOLO

model = YOLO("/home/ubuntu/Coding/swork/bmd-v3.5/models/best.pt")

model.export(format="ncnn", imgsz=320, name="thien_ncnn_model")