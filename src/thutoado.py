import cv2
import numpy as np

class PointCreator:
    def __init__(self):
        # Khởi tạo camera
        self.cap = cv2.VideoCapture(2)
        
        # Thiết lập độ phân giải camera
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # Định nghĩa kích thước thực tế của vùng nhìn camera (mm)
        self.REAL_WIDTH = 220.89   # mm
        self.REAL_HEIGHT = 169.33  # mm
        
        # Lưu trữ điểm được click
        self.points = []
        
        # Tạo cửa sổ và thiết lập callback cho mouse event
        cv2.namedWindow('Create Points')
        cv2.setMouseCallback('Create Points', self.mouse_callback)

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:  # Click chuột trái
            # Lưu điểm pixel
            self.points.append((x, y))
            
            # Tính toán tọa độ thực
            frame_height, frame_width = self.current_frame.shape[:2]
            real_x = (x / frame_width) * self.REAL_WIDTH
            real_y = (y / frame_height) * self.REAL_HEIGHT
            
            # In thông tin
            print(f"\nĐiểm mới:")
            print(f"Tọa độ pixel: ({x}, {y})")
            print(f"Tọa độ thực (mm): ({real_x:.2f}, {real_y:.2f})")

    def draw_points(self, frame):
        # Vẽ tất cả các điểm đã click
        for i, point in enumerate(self.points):
            # Vẽ điểm
            cv2.circle(frame, point, 5, (0, 0, 255), -1)
            
            # Tính toán tọa độ thực
            frame_height, frame_width = frame.shape[:2]
            real_x = (point[0] / frame_width) * self.REAL_WIDTH
            real_y = (point[1] / frame_height) * self.REAL_HEIGHT
            
            # Hiển thị tọa độ
            text = f"({real_x:.1f}, {real_y:.1f})"
            cv2.putText(frame, text, 
                       (point[0] + 10, point[1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        return frame

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Không thể đọc frame từ camera")
                break

            # Lấy kích thước frame
            frame_height, frame_width = frame.shape[:2]
            
            # Lưu frame hiện tại để sử dụng trong callback
            self.current_frame = frame.copy()
            
            # Vẽ các điểm và tọa độ
            frame = self.draw_points(frame)
            
            # Hiển thị thông tin kích thước thực tế
            cv2.putText(frame, f"Kich thuoc thuc: {self.REAL_WIDTH:.1f}mm x {self.REAL_HEIGHT:.1f}mm", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Hiển thị độ phân giải frame
            cv2.putText(frame, f"Do phan giai frame: {frame_width} x {frame_height}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Hiển thị frame
            cv2.imshow('Create Points', frame)
            
            # Phím tắt:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):  # Nhấn 'q' để thoát
                break
            elif key == ord('c'):  # Nhấn 'c' để xóa tất cả điểm
                self.points = []
                print("\nĐã xóa tất cả các điểm")
        
        # Giải phóng tài nguyên
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("Hướng dẫn sử dụng:")
    print("- Click chuột trái để tạo điểm")
    print("- Nhấn 'c' để xóa tất cả các điểm")
    print("- Nhấn 'q' để thoát")
    creator = PointCreator()
    creator.run()