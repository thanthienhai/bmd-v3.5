import cv2
import numpy as np

class PointCreator:
    def __init__(self):
        # Khởi tạo camera
        self.cap = cv2.VideoCapture(2)
        
        # Thiết lập độ phân giải camera
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # Kích thước thực tế của frame (mm)
        self.REAL_WIDTH = 220.89
        self.REAL_HEIGHT = 169.33
        
        # Kích thước máy điều khiển (mm)
        self.MACHINE_X_MAX = 120
        self.MACHINE_Y_MAX = 250
        
        # Tính tỷ lệ chuyển đổi
        self.x_ratio = self.MACHINE_X_MAX / self.REAL_WIDTH
        self.y_ratio = self.MACHINE_Y_MAX / self.REAL_HEIGHT
        
        # Lưu trữ điểm được click
        self.points = []
        
        # Tạo cửa sổ và thiết lập callback cho mouse event
        cv2.namedWindow('Create Points')
        cv2.setMouseCallback('Create Points', self.mouse_callback)

    def convert_to_machine_coordinates(self, real_x, real_y):
        """Chuyển đổi từ tọa độ thực sang tọa độ máy"""
        # Chuyển đổi tọa độ
        machine_x = int(round(real_x * self.x_ratio))
        machine_y = int(round(real_y * self.y_ratio))
        
        # Giới hạn trong phạm vi của máy
        machine_x = min(max(0, machine_x), self.MACHINE_X_MAX)
        machine_y = min(max(0, machine_y), self.MACHINE_Y_MAX)
        
        return machine_x, machine_y

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:  # Click chuột trái
            # Tính toán tọa độ thực
            frame_height, frame_width = self.current_frame.shape[:2]
            real_x = (x / frame_width) * self.REAL_WIDTH
            real_y = (y / frame_height) * self.REAL_HEIGHT
            
            # Chuyển đổi sang tọa độ máy
            machine_x, machine_y = self.convert_to_machine_coordinates(real_x, real_y)
            
            # Lưu điểm và tọa độ
            self.points.append({
                'pixel': (x, y),
                'real': (real_x, real_y),
                'machine': (machine_x, machine_y)
            })
            
            # In thông tin
            print(f"\nĐiểm mới:")
            print(f"Tọa độ pixel: ({x}, {y})")
            print(f"Tọa độ thực (mm): ({real_x:.2f}, {real_y:.2f})")
            print(f"Tọa độ máy (mm): ({machine_x}, {machine_y})")

    def draw_points(self, frame):
        for point in self.points:
            pixel_coord = point['pixel']
            real_coord = point['real']
            machine_coord = point['machine']
            
            # Vẽ điểm
            cv2.circle(frame, pixel_coord, 5, (0, 0, 255), -1)
            
            # Hiển thị tọa độ
            text = f"Real: ({real_coord[0]:.1f}, {real_coord[1]:.1f})"
            cv2.putText(frame, text, 
                       (pixel_coord[0] + 10, pixel_coord[1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                       
            text = f"Machine: ({machine_coord[0]}, {machine_coord[1]})"
            cv2.putText(frame, text, 
                       (pixel_coord[0] + 10, pixel_coord[1] + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return frame

    def run(self):
        print("\nTỷ lệ chuyển đổi:")
        print(f"X: {self.x_ratio:.4f}")
        print(f"Y: {self.y_ratio:.4f}")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Không thể đọc frame từ camera")
                break

            self.current_frame = frame.copy()
            frame = self.draw_points(frame)
            
            # Hiển thị thông tin kích thước
            cv2.putText(frame, f"Kich thuoc thuc: {self.REAL_WIDTH:.1f}mm x {self.REAL_HEIGHT:.1f}mm", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Kich thuoc may: {self.MACHINE_X_MAX}mm x {self.MACHINE_Y_MAX}mm", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Create Points', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                self.points = []
                print("\nĐã xóa tất cả các điểm")
        
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("Hướng dẫn sử dụng:")
    print("- Click chuột trái để tạo điểm")
    print("- Nhấn 'c' để xóa tất cả các điểm")
    print("- Nhấn 'q' để thoát")
    creator = PointCreator()
    creator.run() 