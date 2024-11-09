# processing.py
from ultralytics import YOLO
import cv2

class FootAcupointDetector:
    def __init__(self, model_path):
        # Load the YOLO-Pose model
        self.model = YOLO(model_path)
        # Định nghĩa tên các huyệt đạo
        self.acupoint_names = {
            0: "Ly Noi Dinh",
            1: "Doc Am",
            2: "Ly Hoanh Van", 
            3: "Dung Tuyen",
            4: "Tuc Tam",
            5: "That Mien"
        }

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
        # Vẽ các điểm huyệt lên ảnh và hiển thị tên
        for points in keypoints:
            for idx, (x, y) in enumerate(points):
                if idx >= len(self.acupoint_names):  # Kiểm tra nếu vượt quá số lượng tên đã định nghĩa
                    break
                x, y = int(x), int(y)
                
                # Vẽ điểm keypoint với kích thước lớn hơn (radius = 6 thay vì 3)
                cv2.circle(image, (x, y), 6, (0, 0, 255), -1)  # Vẽ mỗi keypoint như một vòng tròn đỏ lớn hơn
                
                # Lấy tên huyệt đạo
                acupoint_name = self.acupoint_names[idx]
                
                # Tính toán vị trí để đặt text
                text_x = x + 10  # Tăng khoảng cách với điểm để dễ đọc hơn
                text_y = y + 10
                
                # Vẽ tên huyệt đạo trực tiếp không có nền
                cv2.putText(
                    image,
                    acupoint_name,
                    (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,  # Tăng kích thước font để dễ đọc hơn
                    (255, 0, 0),  # Màu trắng
                    2,  # Tăng độ dày để text nổi bật hơn
                    cv2.LINE_AA
                )
        return image