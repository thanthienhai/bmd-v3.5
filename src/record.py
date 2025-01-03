import cv2
import time
import os
from datetime import datetime

class DualCameraRecorder:
    def __init__(self):
        # Khởi tạo camera với độ phân giải cao
        self.cap_left = cv2.VideoCapture(2)  # Camera trái
        self.cap_right = cv2.VideoCapture(4)  # Camera phải

        # Thiết lập độ phân giải cho camera
        self.width = 1280
        self.height = 720
        self.cap_left.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap_left.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap_right.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap_right.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        # Tạo thư mục frames trong src
        self.save_dir = os.path.join(os.path.dirname(__file__), "frames")
        os.makedirs(self.save_dir, exist_ok=True)

        # Thiết lập video writer
        self.video_writer_left = None
        self.video_writer_right = None
        self.is_recording = False
        self.fps = 30
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')

    def start_recording(self):
        """Bắt đầu ghi video"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        left_video_path = os.path.join(self.save_dir, f"left_{timestamp}.avi")
        right_video_path = os.path.join(self.save_dir, f"right_{timestamp}.avi")
        
        self.video_writer_left = cv2.VideoWriter(
            left_video_path, 
            self.fourcc, 
            self.fps, 
            (self.height, self.width)  # Đảo ngược width và height do xoay frame
        )
        
        self.video_writer_right = cv2.VideoWriter(
            right_video_path, 
            self.fourcc, 
            self.fps, 
            (self.height, self.width)
        )
        
        self.is_recording = True
        print(f"Bắt đầu ghi video: {left_video_path} và {right_video_path}")

    def stop_recording(self):
        """Dừng ghi video"""
        if self.video_writer_left is not None:
            self.video_writer_left.release()
        if self.video_writer_right is not None:
            self.video_writer_right.release()
            
        self.is_recording = False
        print("Đã dừng ghi video")

    def capture_frames(self):
        """Chụp và hiển thị frame từ cả hai camera"""
        try:
            while True:
                ret_left, frame_left = self.cap_left.read()
                ret_right, frame_right = self.cap_right.read()

                if ret_left and ret_right:
                    # Xoay frame 90 độ theo chiều kim đồng hồ
                    frame_left = cv2.rotate(frame_left, cv2.ROTATE_90_CLOCKWISE)
                    frame_right = cv2.rotate(frame_right, cv2.ROTATE_90_CLOCKWISE)

                    # Ghi video nếu đang recording
                    if self.is_recording:
                        self.video_writer_left.write(frame_left)
                        self.video_writer_right.write(frame_right)

                    # Hiển thị frame
                    cv2.imshow('Camera trai', frame_left)
                    cv2.imshow('Camera phai', frame_right)

                    # Đọc phím nhấn
                    key = cv2.waitKey(1) & 0xFF

                    # Nhấn 's' để lưu ảnh
                    if key == ord('s'):
                        self.save_frames(frame_left, frame_right)
                    # Nhấn 'r' để bắt đầu/dừng ghi video
                    elif key == ord('r'):
                        if self.is_recording:
                            self.stop_recording()
                        else:
                            self.start_recording()
                    # Nhấn 'q' để thoát
                    elif key == ord('q'):
                        break
                else:
                    print("Không thể đọc frame từ camera")
                    break

        finally:
            self.release()
            self.stop_recording()  # Đảm bảo dừng ghi video khi thoát

    def save_frames(self, frame_left, frame_right):
        """Lưu frame từ cả hai camera"""
        try:
            # Tạo tên file với timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            left_filename = os.path.join(self.save_dir, f"left_{timestamp}.jpg")
            right_filename = os.path.join(self.save_dir, f"right_{timestamp}.jpg")

            # Lưu ảnh
            cv2.imwrite(left_filename, frame_left)
            cv2.imwrite(right_filename, frame_right)
            print(f"Đã lưu ảnh: {left_filename} và {right_filename}")

        except Exception as e:
            print(f"Lỗi khi lưu ảnh: {str(e)}")

    def release(self):
        """Giải phóng tài nguyên"""
        self.stop_recording()  # Đảm bảo dừng ghi video
        self.cap_left.release()
        self.cap_right.release()
        cv2.destroyAllWindows()

def main():
    recorder = DualCameraRecorder()
    print("Hướng dẫn:")
    print("- Nhấn 's' để lưu ảnh")
    print("- Nhấn 'r' để bắt đầu/dừng ghi video")
    print("- Nhấn 'q' để thoát")
    recorder.capture_frames()

if __name__ == "__main__":
    main()