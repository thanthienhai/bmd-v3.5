'''
    CODE KIỂM TRA CHIỀU DÀI, CHIỀU RỘNG CỦA ẢNH TRÊN THỰC TẾ SỬ DỤNG THẺ TÍN DỤNG 
'''
# import cv2
# import numpy as np

# def measure_real_size():
#     # Kích thước chuẩn của thẻ tín dụng (đơn vị mm)
#     CARD_WIDTH_MM = 85.60
#     CARD_HEIGHT_MM = 53.98
    
#     # Khởi tạo webcam
#     cap = cv2.VideoCapture(0)
    
#     if not cap.isOpened():
#         print("Không thể mở webcam")
#         return
    
#     try:
#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 print("Không thể đọc frame")
#                 break
                
#             # Chuyển sang ảnh grayscale
#             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
#             # Làm mờ ảnh để giảm nhiễu
#             blurred = cv2.GaussianBlur(gray, (7, 7), 0)
            
#             # Phát hiện cạnh
#             edges = cv2.Canny(blurred, 50, 150)
            
#             # Tìm các contour
#             contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
#             # Vẽ khung và hiển thị hướng dẫn
#             cv2.putText(frame, "Dat the tin dung vao khung", (10, 30),
#                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
#             for contour in contours:
#                 # Lọc các contour quá nhỏ
#                 if cv2.contourArea(contour) < 5000:
#                     continue
                    
#                 # Tìm hình chữ nhật xấp xỉ
#                 rect = cv2.minAreaRect(contour)
#                 box = cv2.boxPoints(rect)
#                 box = np.array(box, dtype=np.int32)  # Sử dụng np.int32 thay vì np.int0
                
#                 # Tính kích thước theo pixel
#                 width_px = rect[1][0]
#                 height_px = rect[1][1]
                
#                 # Tính tỉ lệ chuyển đổi (mm/pixel)
#                 width_ratio = CARD_WIDTH_MM / width_px
#                 height_ratio = CARD_HEIGHT_MM / height_px
                
#                 # Lấy kích thước thực của frame
#                 frame_height, frame_width = frame.shape[:2]
#                 real_width = frame_width * width_ratio
#                 real_height = frame_height * height_ratio
                
#                 # Vẽ contour và hiển thị kích thước
#                 cv2.drawContours(frame, [box], 0, (0, 255, 0), 2)
#                 cv2.putText(frame, f"Kich thuoc thuc: {real_width:.1f}mm x {real_height:.1f}mm",
#                            (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
#             # Hiển thị frame
#             cv2.imshow('Measurement', frame)
            
#             # Nhấn 'q' để thoát
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
                
#     finally:
#         cap.release()
#         cv2.destroyAllWindows()

# if __name__ == "__main__":
#     measure_real_size()

'''
    CODE KIỂM TRA ĐỘ PHÂN GIẢI CAO NHẤT MÀ WEBCAM HỖ TRỢ
'''

import cv2

def get_max_resolution():
    # Danh sách các độ phân giải phổ biến (theo thứ tự từ cao đến thấp)
    standard_resolutions = [
        (3840, 2160),  # 4K
        (2560, 1440),  # QHD
        (1920, 1080),  # Full HD
        (1280, 720),   # HD
        (1024, 576),    # nHD
        (800, 600),    # SVGA
        (640, 480),    # VGA
        (320, 240),    # QVGA
    ]

    cap = cv2.VideoCapture(0)  # Mở webcam (thường là 0, có thể thay đổi tùy hệ thống)

    if not cap.isOpened():
        print("Không thể mở webcam")
        return

    max_width = 0
    max_height = 0

    for resolution in standard_resolutions:
        width, height = resolution
        # Thử thiết lập độ phân giải
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # Đọc một frame để kiểm tra
        ret, frame = cap.read()
        if not ret:
            print(f"Không thể đọc frame với độ phân giải {width}x{height}")
            continue

        # Kiểm tra độ phân giải thực tế
        actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        if actual_width >= width and actual_height >= height:
            max_width = int(actual_width)
            max_height = int(actual_height)
            print(f"Độ phân giải được hỗ trợ: {max_width}x{max_height}")
            break  # Nếu tìm thấy độ phân giải phù hợp, dừng lại

    cap.release()

    if max_width and max_height:
        print(f"Độ phân giải cao nhất mà webcam hỗ trợ: {max_width}x{max_height}")
    else:
        print("Không tìm thấy độ phân giải nào được hỗ trợ.")

if __name__ == "__main__":
    get_max_resolution()
