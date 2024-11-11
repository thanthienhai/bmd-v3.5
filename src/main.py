import cv2
from processing import FootAcupointDetector

def main(video_path):
    # Mở video
    # cap = cv2.VideoCapture(video_path)
    cap = cv2.VideoCapture('/dev/video0')
    if not cap.isOpened():
        raise Exception(f"Error: Could not open video file {video_path}")
        
    # Thiết lập độ phân giải Full HD
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    # Kiểm tra xem camera có hỗ trợ độ phân giải này không
    actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"Actual resolution: {actual_width}x{actual_height}")

    # Khởi tạo model
    detector = FootAcupointDetector(model_path='models/foot-keypoints-v7i.pt')
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

            # Hiển thị kết quả (có thể resize để hiển thị cho phù hợp với màn hình)
            display_image = cv2.resize(output_image, (1280, 720))  # resize để dễ xem
            cv2.imshow('Foot Acupoint Detection', display_image)

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