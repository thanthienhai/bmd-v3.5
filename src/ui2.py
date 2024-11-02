import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2

# Giả định rằng lớp FootAcupointDetector đã được định nghĩa
class FootAcupointDetector:
    def __init__(self, model_path):
        # Tải mô hình YOLO từ model_path (giả định)
        pass

    def detect_acupoints(self, frame):
        # Phát hiện điểm huyệt trên frame (giả định)
        # Trả về danh sách keypoints (giả định)
        return []

    def visualize_keypoints(self, frame, keypoints):
        # Hiển thị các điểm huyệt lên hình ảnh (giả định)
        # Ví dụ vẽ điểm trên frame
        for (x, y) in keypoints:
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
        return frame


class BMDMachineControl:
    def __init__(self, root, video_path):
        self.root = root
        self.root.title("BMD machine control V3.5")
        self.video_path = video_path

        # Mở video
        self.cap = cv2.VideoCapture(self.video_path)

        # Kiểm tra xem video có mở được không
        if not self.cap.isOpened():
            raise Exception(f"Error: Could not open video file {self.video_path}")

        # Khởi tạo model phát hiện điểm huyệt
        self.detector = FootAcupointDetector(model_path='models/yolo_pose_model.pt')

        # Tạo giao diện tab
        tab_control = ttk.Notebook(root)
        tab1 = ttk.Frame(tab_control)
        tab2 = ttk.Frame(tab_control)
        tab3 = ttk.Frame(tab_control)
        
        tab_control.add(tab1, text='Massage bàn chân')
        tab_control.add(tab2, text='Tạo bài bấm huyệt')
        tab_control.add(tab3, text='Cài đặt')
        tab_control.pack(expand=1, fill='both')
        
        # Khung nội dung chính cho tab 1
        main_frame = ttk.Frame(tab1)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Display Frame - Top Section
        display_frame = ttk.Frame(main_frame)
        display_frame.pack(fill='x', pady=(0, 20))
        
        # Left foot display
        left_frame = ttk.LabelFrame(display_frame, text="the screen display of the left foot")
        left_frame.pack(side=tk.LEFT, fill='both', expand=True, padx=5)
        self.left_display = ttk.Label(left_frame, relief='solid', borderwidth=1)
        self.left_display.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Right foot display (sử dụng nếu cần thiết)
        right_frame = ttk.LabelFrame(display_frame, text="the screen display of the right foot")
        right_frame.pack(side=tk.LEFT, fill='both', expand=True, padx=5)
        self.right_display = ttk.Label(right_frame, relief='solid', borderwidth=1)
        self.right_display.pack(fill='both', expand=True, padx=5, pady=5)

        # Gọi hàm hiển thị video
        self.show_frame()

    def show_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Thực hiện suy luận để nhận diện điểm huyệt
            keypoints = self.detector.detect_acupoints(frame)

            # Hiển thị các điểm huyệt lên hình ảnh
            output_image = self.detector.visualize_keypoints(frame, keypoints)

            # Chuyển đổi từ BGR sang RGB
            frame_rgb = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)
            # Chuyển đổi khung hình thành đối tượng ImageTk
            image = Image.fromarray(frame_rgb)
            image = image.resize((300, 200))  # Điều chỉnh kích thước nếu cần
            photo = ImageTk.PhotoImage(image)
            
            # Cập nhật khung hình trên giao diện
            self.left_display.config(image=photo)
            self.left_display.image = photo  # Giữ tham chiếu để tránh bị xóa bộ nhớ
            
            # Tiếp tục cập nhật khung hình sau 30ms
            self.root.after(30, self.show_frame)
        else:
            # Kết thúc nếu không có khung hình nào
            self.cap.release()

if __name__ == "__main__":
    video_path = "your_video_path_here.mp4"  # Thay bằng đường dẫn video của bạn
    root = tk.Tk()
    app = BMDMachineControl(root, video_path)
    root.mainloop()
