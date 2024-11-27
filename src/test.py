import cv2
from ultralytics import YOLO
import numpy as np

def process_video(video_path, model_path='yolov8n-pose.pt'):
    """
    Thực hiện inference YOLO Pose trên video và in ra tọa độ keypoint
    
    Args:
        video_path (str): Đường dẫn tới file video
        model_path (str): Đường dẫn tới weights model YOLO Pose
    """
    # Tải model YOLO Pose
    model = YOLO('models/best-640-100eps.pt')
    
    # Mở video
    cap = cv2.VideoCapture(video_path)
    
    # Kiểm tra video mở thành công
    if not cap.isOpened():
        print("Lỗi: Không thể mở video")
        return
    
    frame_count = 0
    while cap.isOpened():
        # Đọc từng frame
        ret, frame = cap.read()
        
        # Kết thúc nếu không còn frame
        if not ret:
            break
        
        frame_count += 1
        
        # Thực hiện inference
        results = model(frame, stream=True)
        
        for result in results:
            # Lấy keypoints từ kết quả
            keypoints = result.keypoints
            
            # In thông tin keypoints cho từng người
            for i, kpts in enumerate(keypoints):
                print(f"Frame {frame_count}, Người {i+1}:")
                
                # In từng keypoint
                for j, kp in enumerate(kpts.xy[0]):
                    x, y = kp.tolist()
                    print(f"  Keypoint {j}: (x: {x:.2f}, y: {y:.2f})")
                
                print("---")
        
        # Tùy chọn: hiển thị video
        cv2.imshow('YOLO Pose', frame)
        
        # Nhấn 'q' để thoát
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Giải phóng tài nguyên
    cap.release()
    cv2.destroyAllWindows()

# Sử dụng
video_path = '/home/thanthien/Coding/bmd-v3.5/video_test/1.mp4'
process_video(video_path)