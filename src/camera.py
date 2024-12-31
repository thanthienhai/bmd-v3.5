import cv2
import numpy as np

# Kích thước thực tế của thẻ căn cước (đơn vị: mm)
card_width_mm = 85.6
card_height_mm = 53.98

# Danh sách để lưu các điểm đánh dấu
points = []

# Hàm xử lý sự kiện nhấp chuột
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        # Lưu tọa độ điểm nhấp chuột
        points.append((x, y))
        # Vẽ một vòng tròn nhỏ tại điểm nhấp chuột
        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow('Webcam', frame)

        # Nếu đã chọn đủ 4 điểm, tính toán kích thước
        if len(points) == 4:
            calculate_real_size()

# Hàm tính kích thước thực tế
def calculate_real_size():
    # Sắp xếp các điểm theo thứ tự: trên-trái, trên-phải, dưới-phải, dưới-trái
    sorted_points = sort_points(points)

    # Tính chiều rộng và chiều cao trong ảnh (đơn vị: pixel)
    width_pixels = np.linalg.norm(np.array(sorted_points[1]) - np.array(sorted_points[0]))
    height_pixels = np.linalg.norm(np.array(sorted_points[2]) - np.array(sorted_points[1]))

    # Tính tỷ lệ giữa kích thước thực tế và kích thước pixel
    width_ratio = card_width_mm / width_pixels
    height_ratio = card_height_mm / height_pixels

    print(f"Tỷ lệ kích thước thực tế so với pixel:")
    print(f"Chiều rộng: {width_ratio:.4f} mm/pixel")
    print(f"Chiều cao: {height_ratio:.4f} mm/pixel")

    # Tính kích thước thực tế của ảnh chụp
    height, width, _ = frame.shape
    real_width = width * width_ratio
    real_height = height * height_ratio

    print(f"Kích thước thực tế của ảnh chụp từ webcam:")
    print(f"Chiều rộng: {real_width:.2f} mm")
    print(f"Chiều cao: {real_height:.2f} mm")

# Hàm sắp xếp các điểm theo thứ tự: trên-trái, trên-phải, dưới-phải, dưới-trái
def sort_points(pts):
    pts = np.array(pts, dtype="float32")
    rect = np.zeros((4, 2), dtype="float32")

    # Tổng của tọa độ (x + y) sẽ nhỏ nhất cho điểm trên-trái và lớn nhất cho điểm dưới-phải
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # Trên-trái
    rect[2] = pts[np.argmax(s)]  # Dưới-phải

    # Hiệu của tọa độ (x - y) sẽ nhỏ nhất cho điểm trên-phải và lớn nhất cho điểm dưới-trái
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # Trên-phải
    rect[3] = pts[np.argmax(diff)]  # Dưới-trái

    return rect

# Mở webcam
cap = cv2.VideoCapture(2)

if not cap.isOpened():
    print("Không thể mở webcam")
    exit()

# Đọc frame từ webcam
ret, frame = cap.read()
if not ret:
    print("Không thể đọc frame từ webcam")
    cap.release()
    exit()

# Hiển thị frame và chờ người dùng đánh dấu 4 góc
cv2.imshow('Webcam', frame)
cv2.setMouseCallback('Webcam', click_event)

# Chờ người dùng nhấn phím 'q' để thoát
while True:
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Giải phóng webcam và đóng cửa sổ hiển thị
cap.release()
cv2.destroyAllWindows()