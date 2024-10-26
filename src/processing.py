# processing.py

from ultralytics import YOLO
import cv2

class FootAcupointDetector:
    def __init__(self, model_path):
        # Load the YOLO-Pose model
        self.model = YOLO(model_path)

    def detect_acupoints(self, image):
        # Perform inference
        results = self.model(image)

        # Extract bounding boxes and keypoints
        keypoints = []
        for result in results:
            if result.keypoints is not None:  # Kiểm tra nếu có keypoints
                for detection in result.keypoints.xy:  # Lấy tọa độ x, y của các keypoints
                    points = detection.cpu().numpy()  # Chuyển thành numpy array để xử lý
                    keypoints.append(points)
        return keypoints

    def visualize_keypoints(self, image, keypoints):
        # Vẽ các điểm huyệt lên ảnh
        for points in keypoints:
            for (x, y) in points:  # Duyệt qua từng cặp (x, y)
                x, y = int(x), int(y)
                cv2.circle(image, (x, y), 3, (0, 0, 255), -1)  # Vẽ mỗi keypoint như một vòng tròn đỏ
        return image
