# # main.py

# import cv2
# from src.camera import get_camera, capture_frame, release_camera
# from src.processing import FootAcupointDetector

# def main():
#     # Khởi tạo camera và model
#     cap = get_camera()  # Mở camera
#     detector = FootAcupointDetector(model_path='models/yolo_pose_model.pt')

#     try:
#         while True:
#             # Chụp ảnh từ camera
#             frame = capture_frame(cap)

#             # Thực hiện suy luận để nhận diện điểm huyệt
#             keypoints = detector.detect_acupoints(frame)

#             # Hiển thị các điểm huyệt trên hình ảnh
#             output_image = detector.visualize_keypoints(frame, keypoints)

#             # Hiển thị kết quả
#             cv2.imshow('Foot Acupoint Detection', output_image)

#             # Thoát bằng phím 'q'
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
#     except Exception as e:
#         print(f"An error occurred: {e}")
#     finally:
#         # Giải phóng tài nguyên
#         release_camera(cap)
#         cv2.destroyAllWindows()

# if __name__ == '__main__':
#     main()

# main.py

import cv2
from processing import FootAcupointDetector

def main(video_path):
    # Mở video
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise Exception(f"Error: Could not open video file {video_path}")

    # Khởi tạo model
    detector = FootAcupointDetector(model_path='models/yolo_pose_model.pt')

    try:
        while True:
            # Đọc từng frame từ video
            ret, frame = cap.read()
            if not ret:
                print("End of video reached or cannot fetch the frame.")
                break

            # Thực hiện suy luận để nhận diện điểm huyệt
            keypoints = detector.detect_acupoints(frame)

            # Hiển thị các điểm huyệt trên hình ảnh
            output_image = detector.visualize_keypoints(frame, keypoints)

            # Hiển thị kết quả
            cv2.imshow('Foot Acupoint Detection', output_image)

            # Tạm dừng khung hình (tốc độ phát lại video); nhấn 'q' để thoát
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Giải phóng tài nguyên
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    video_path = 'video_test/video.mp4'  # Đường dẫn tới video của bạn
    main(video_path)
