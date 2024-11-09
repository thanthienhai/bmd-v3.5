import cv2
from processing import FootAcupointDetector

def main(video_path):
    # Mở video
    cap = cv2.VideoCapture(video_path)
    # cap = cv2.VideoCapture('/dev/video4')
    if not cap.isOpened():
        raise Exception(f"Error: Could not open video file {video_path}")

    # Khởi tạo model
    detector = FootAcupointDetector(model_path='models/best_9_11.pt')
    # detector = FootAcupointDetector(model_path='/home/ubuntu/Coding/swork/bmd-v3.5/models/best_ncnn_model')

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
    video_path = 'video_test/1.mp4'  # Đường dẫn tới video của bạn
    main(video_path)
