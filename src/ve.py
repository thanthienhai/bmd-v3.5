import cv2

class RectangleDrawer:
    def __init__(self, image_path):
        # Đọc ảnh từ file
        self.image = cv2.imread(image_path)
        if self.image is None:
            print(f"Không thể đọc ảnh từ {image_path}")
            exit(1)

        # Tạo bản sao của ảnh gốc
        self.clone = self.image.copy()

        # Biến lưu trạng thái vẽ
        self.drawing = False
        self.ix, self.iy = -1, -1
        self.fx, self.fy = -1, -1

        # Kích thước hình chữ nhật cố định
        # self.fixed_width = 1140
        # self.fixed_height = 560
        self.fixed_width = 1145
        self.fixed_height = 578

        # Tạo cửa sổ và thiết lập callback
        cv2.namedWindow('Image')
        cv2.setMouseCallback('Image', self.draw_rectangle)

    def draw_fixed_rectangle(self, frame):
        """Vẽ hình chữ nhật cố định vào giữa ảnh"""
        height, width = frame.shape[:2]
        x_start = int((width - self.fixed_width) / 2)
        y_start = int((height - self.fixed_height) / 2)
        x_end = x_start + self.fixed_width
        y_end = y_start + self.fixed_height
        
        # Vẽ hình chữ nhật cố định màu đỏ
        cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), (0, 0, 255), 2)
        
        # Hiển thị thông tin kích thước
        text = f"Fixed: {self.fixed_width}x{self.fixed_height}"
        cv2.putText(frame, text, (x_start, y_start - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    def draw_rectangle(self, event, x, y, flags, param):
        # Xử lý sự kiện chuột
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix, self.iy = x, y

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.clone = self.image.copy()
                self.draw_fixed_rectangle(self.clone)
                cv2.rectangle(self.clone, (self.ix, self.iy), (x, y), (0, 255, 0), 2)

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.fx, self.fy = x, y
            self.clone = self.image.copy()
            self.draw_fixed_rectangle(self.clone)
            cv2.rectangle(self.clone, (self.ix, self.iy), (self.fx, self.fy), (0, 255, 0), 2)
            
            # Tính toán tọa độ 4 điểm
            x1 = min(self.ix, self.fx)
            y1 = min(self.iy, self.fy)
            x2 = max(self.ix, self.fx)
            y2 = max(self.iy, self.fy)
            
            # Tọa độ 4 góc
            top_left = (x1, y1)
            top_right = (x2, y1)
            bottom_left = (x1, y2)
            bottom_right = (x2, y2)
            
            # Hiển thị thông tin
            print("Tọa độ 4 điểm của hình chữ nhật:")
            print(f"1. Góc trên trái: {top_left}")
            print(f"2. Góc trên phải: {top_right}")
            print(f"3. Góc dưới trái: {bottom_left}")
            print(f"4. Góc dưới phải: {bottom_right}")
            
            # Vẽ các điểm và hiển thị tọa độ
            for i, point in enumerate([top_left, top_right, bottom_left, bottom_right]):
                cv2.circle(self.clone, point, 5, (255, 0, 0), -1)
                cv2.putText(self.clone, f"{i+1}:{point}", (point[0] + 10, point[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

        cv2.imshow('Image', self.clone)

    def run(self):
        # Vẽ hình chữ nhật cố định ban đầu
        self.draw_fixed_rectangle(self.clone)
        
        while True:
            cv2.imshow('Image', self.clone)
            key = cv2.waitKey(1) & 0xFF
            
            # Nhấn 'r' để reset
            if key == ord('r'):
                self.clone = self.image.copy()
                self.draw_fixed_rectangle(self.clone)
            
            # Nhấn 'q' để thoát
            elif key == ord('q'):
                break

        cv2.destroyAllWindows()

if __name__ == "__main__":
    # Đường dẫn đến ảnh
    image_path = "/home/ubuntu/Coding/swork/bmd-v3.5/src/webcam2_frame_9.jpg"  # Thay đổi đường dẫn này
    
    print("Chương trình vẽ hình chữ nhật trên ảnh")
    print("Hướng dẫn:")
    print("- Hình chữ nhật cố định 1140x560 (màu đỏ)")
    print("- Kéo chuột để vẽ hình chữ nhật (màu xanh lá)")
    print("- Nhấn 'r' để reset")
    print("- Nhấn 'q' để thoát")
    drawer = RectangleDrawer(image_path)
    drawer.run() 