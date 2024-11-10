# BMD Machine Control V3.5

## Mô tả
BMD Machine Control V3.5 là một ứng dụng GUI được phát triển bằng Python, sử dụng thư viện Tkinter để nhận diện huyệt đạo trên lòng bàn chân thông qua camera hoặc video. Ứng dụng sử dụng mô hình YOLO-Pose để phát hiện các điểm huyệt đạo và hiển thị chúng trên giao diện người dùng.

## Tính năng
- Nhận diện huyệt đạo trên lòng bàn chân.
- Hiển thị video từ camera hoặc video test.
- Tính năng dừng và bắt đầu quá trình nhận diện.
- Giao diện người dùng thân thiện và dễ sử dụng.
- Chế độ toàn màn hình cho trải nghiệm tốt hơn.

## Yêu cầu
- Python 3.7 trở lên
- Thư viện cần thiết:
  - `tkinter`
  - `opencv-python`
  - `Pillow`
  - `ultralytics` (cho mô hình YOLO)
  
## Cài đặt
1. **Clone repository**:
   ```bash
   git clone https://github.com/yourusername/BMD-Machine-Control.git
   cd BMD-Machine-Control
   ```

2. **Cài đặt các thư viện cần thiết**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Tải mô hình YOLO**:
   - Tải mô hình YOLO-Pose và lưu vào thư mục `models/` với tên `best-640-100eps.pt`.

## Cấu trúc thư mục

BMD-Machine-Control/
│
├── src/
│ ├── ui.py # Giao diện người dùng
│ ├── processing.py # Xử lý nhận diện huyệt đạo
│ └── main.py # Điểm khởi đầu của ứng dụng
│
├── models/ # Thư mục chứa mô hình YOLO
│ └── best-640-100eps.pt # Mô hình YOLO-Pose
│
├── requirements.txt # Danh sách các thư viện cần thiết
└── README.md # Tài liệu hướng dẫn


## Cách sử dụng
1. **Khởi động ứng dụng**:
   - Chạy file `main.py`:
   ```bash
   python src/main.py
   ```

2. **Sử dụng giao diện**:
   - Nhấn nút "Bắt đầu" để bắt đầu nhận diện huyệt đạo.
   - Nhấn nút "Dừng" để dừng quá trình nhận diện.
   - Nhấn nút "X" trên góc phải để thoát khỏi ứng dụng.

## Ghi chú
- Đảm bảo camera hoặc video test được kết nối và hoạt động bình thường trước khi bắt đầu nhận diện.
- Nếu gặp lỗi trong quá trình nhận diện, hãy kiểm tra lại đường dẫn đến mô hình YOLO và đảm bảo rằng các thư viện đã được cài đặt đúng cách.

## Tài liệu tham khảo
- [YOLO (You Only Look Once)](https://pjreddie.com/darknet/yolo/)
- [OpenCV Documentation](https://docs.opencv.org/)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)

## Giấy phép
Dự án này được cấp phép theo Giấy phép MIT. Xem file LICENSE để biết thêm chi tiết.