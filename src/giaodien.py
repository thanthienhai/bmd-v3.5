import tkinter as tk
from tkinter import ttk
import cv2
from ultralytics import YOLO
import time
from PIL import Image, ImageTk
import threading
import numpy as np
import json
from uart import UARTManager

class MedicalControlApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.window.attributes("-fullscreen", True)
        self.window.bind("<Escape>", self.toggle_fullscreen)

        style = ttk.Style()
        style.theme_use('clam')

        style.configure("TButton", font=("Arial", 14), padding=2)
        style.map("OnButton.TButton",
                  foreground=[('pressed', 'white'), ('active', 'white')],
                  background=[('pressed', 'green'), ('active', 'green')])
        style.map("OffButton.TButton",
                  foreground=[('pressed', 'white'), ('active', 'white')],
                  background=[('pressed', 'red'), ('active', 'red')])

        self.combo_font = ("Arial", 16)
        style.configure("Large.TCombobox", font=self.combo_font)

        # Model YOLO-pose
        # self.model = YOLO('/home/ubuntu/Coding/swork/bmd-v3.5/models/last.pt')
        # self.model = YOLO('/home/ubuntu/Coding/swork/bmd-v3.5/models/best-1-1-24.pt')
        self.model = YOLO('/home/ubuntu/Coding/swork/bmd-v3.5/models/best-v9.pt')
        self.model.conf = 0.5

        # Thiết lập camera với độ phân giải cao hơn
        self.cap_left = cv2.VideoCapture(4)
        self.cap_right = cv2.VideoCapture(2)
        # self.cap_left = cv2.VideoCapture('/home/ubuntu/Coding/swork/bmd-v3.5/output1.avi')
        # self.cap_right = cv2.VideoCapture('/home/ubuntu/Coding/swork/bmd-v3.5/output1.avi')

        # Thiết lập độ phân giải cho camera
        self.cap_left.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap_left.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap_right.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap_right.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # In ra thông tin về kích thước thực tế của frame
        ret_left, frame_left = self.cap_left.read()
        ret_right, frame_right = self.cap_right.read()
        
        if ret_left and ret_right:
            print(f"Camera trái: {frame_left.shape}")
            print(f"Camera phải: {frame_right.shape}")
        
        self.best_frame_left = None
        self.best_frame_right = None
        self.best_conf_left = 0
        self.best_conf_right = 0

        self.is_detecting = False
        self.detection_start_time = 0

        self.uart = UARTManager(baudrate=115200)
        if not self.uart.is_connected:
            print("Cảnh báo: Không thể kết nối UART")
            
        self.create_gui()

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        is_fullscreen = self.window.attributes("-fullscreen")
        self.window.attributes("-fullscreen", not is_fullscreen)

    def create_gui(self):
        main_frame = ttk.Frame(self.window, padding=2)
        main_frame.grid(row=0, column=0, sticky="NSEW")

        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)

        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)

        camera_frame = ttk.LabelFrame(main_frame, text="Hiển thị camera", padding=2)
        camera_frame.grid(row=0, column=0, sticky="NSEW", padx=(0, 10), pady=5)

        camera_frame.columnconfigure(0, weight=1)
        camera_frame.columnconfigure(1, weight=1)
        camera_frame.rowconfigure(0, weight=1)

        left_camera_frame = ttk.LabelFrame(camera_frame, text="Chân trái", padding=2)
        left_camera_frame.grid(row=0, column=0, sticky="NSEW", padx=5, pady=5)
        self.canvas_left = tk.Canvas(left_camera_frame, bg="black")
        self.canvas_left.pack(expand=True, fill='both')

        right_camera_frame = ttk.LabelFrame(camera_frame, text="Chân phải", padding=2)
        right_camera_frame.grid(row=0, column=1, sticky="NSEW", padx=5, pady=5)
        self.canvas_right = tk.Canvas(right_camera_frame, bg="black")
        self.canvas_right.pack(expand=True, fill='both')

        control_frame = ttk.LabelFrame(main_frame, text="Điều khiển", padding=2)
        control_frame.grid(row=0, column=1, sticky="NSEW", pady=5)

        control_frame.columnconfigure(0, weight=2)

        treatment_label = ttk.Label(control_frame, text="Chọn bài bấm huyệt:", font=("Arial", 16))
        treatment_label.grid(row=0, column=0, sticky="W", pady=(0, 5))
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Large.TCombobox",
                font=("Arial", 20),
                padding=10)

        # Tạo frame riêng cho radio buttons
        radio_frame = ttk.Frame(control_frame)
        radio_frame.grid(row=1, column=0, sticky="EW", pady=(0, 10))

        # Biến để lưu giá trị radio button
        self.treatment_var = tk.StringVar(value="1")  # Giá trị mặc định

        # Style cho radio buttons
        style = ttk.Style()
        style.configure("Custom.TRadiobutton", 
                       font=("Arial", 14),
                       padding=5)

        # Danh sách các bài bấm huyệt và giá trị tương ứng
        treatments = [
            ("Sốt, co giật", "1"),
            ("Stress", "2"),
            ("Thoát vị đĩa đệm", "3"),
            ("Bổ thận tráng dương", "4"),
            ("Nâng cao sức khỏe", "5")
        ]

        # Tạo radio buttons
        for i, (text, value) in enumerate(treatments):
            radio = ttk.Radiobutton(
                radio_frame,
                text=text,
                value=value,
                variable=self.treatment_var,
                style="Custom.TRadiobutton"
            )
            radio.grid(row=i, column=0, sticky="W", padx=20, pady=2)

        main_buttons_frame = ttk.LabelFrame(control_frame, text="Điều khiển chính", padding=2)
        main_buttons_frame.grid(row=2, column=0, sticky="EW", pady=5)

        detect_button = ttk.Button(
            main_buttons_frame,
            text="Nhận diện huyệt",
            command=self.start_detection
        )
        detect_button.grid(row=0, column=0, padx=5, pady=5, sticky="EW", ipadx=5)

        start_press_button = ttk.Button(
            main_buttons_frame,
            text="Bắt đầu bấm huyệt",
            command=self.start_pressing
        )
        start_press_button.grid(row=0, column=1, padx=5, pady=5, sticky="EW", ipadx=5)

        stop_button = ttk.Button(
            main_buttons_frame,
            text="Dừng máy",
            command=self.stop_machine
        )
        stop_button.grid(row=0, column=2, padx=5, pady=5, sticky="EW", ipadx=5)

        main_buttons_frame.columnconfigure(0, weight=1)
        main_buttons_frame.columnconfigure(1, weight=1)
        main_buttons_frame.columnconfigure(2, weight=1)

        medicine_frame = ttk.LabelFrame(control_frame, text="Điều khiển dẫn dược", padding=2)
        medicine_frame.grid(row=3, column=0, sticky="EW", pady=5)

        start_medicine_button = ttk.Button(
            medicine_frame,
            text="Bật dẫn dược",
            style="OnButton.TButton",
            command=self.start_medicine
        )
        start_medicine_button.grid(row=0, column=0, padx=5, pady=5, sticky="EW", ipadx=5)

        stop_medicine_button = ttk.Button(
            medicine_frame,
            text="Tắt dẫn dược",
            style="OffButton.TButton",
            command=self.stop_medicine
        )
        stop_medicine_button.grid(row=0, column=1, padx=5, pady=5, sticky="EW", ipadx=5)

        medicine_frame.columnconfigure(0, weight=1)
        medicine_frame.columnconfigure(1, weight=1)

        burning_frame = ttk.LabelFrame(control_frame, text="Điều khiển đốt dược liệu", padding=2)
        burning_frame.grid(row=4, column=0, sticky="EW", pady=5)

        burn_button = ttk.Button(
            burning_frame,
            text="Đốt dược liệu",
            style="OnButton.TButton",
            command=self.burn_medicine
        )
        burn_button.grid(row=0, column=0, padx=5, pady=5, sticky="EW", ipadx=5)

        stop_burn_button = ttk.Button(
            burning_frame,
            text="Tắt đốt dược liệu",
            style="OffButton.TButton",
            command=self.stop_burn_medicine
        )
        stop_burn_button.grid(row=0, column=1, padx=5, pady=5, sticky="EW", ipadx=5)

        burning_frame.columnconfigure(0, weight=1)
        burning_frame.columnconfigure(1, weight=1)

        exit_button = ttk.Button(
            control_frame,
            text="THOÁT",
            command=self.on_closing
        )
        exit_button.grid(row=5, column=0, sticky="EW", pady=15, ipadx=5)

        self.status_var = tk.StringVar()
        self.status_var.set("Sẵn sàng")
        status_bar = ttk.Label(
            self.window,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=2
        )
        status_bar.grid(row=1, column=0, sticky="EW")

        self.update_frames()

    def start_detection(self):
        if not self.is_detecting:
            self.is_detecting = True
            self.detection_start_time = time.time()
            self.best_conf_left = 0
            self.best_conf_right = 0
            self.best_frame_left = None
            self.best_frame_right = None
            self.status_var.set("Đang nhận diện huyệt...")
            threading.Thread(target=self.detection_thread, daemon=True).start()

    def detection_thread(self):
        while self.is_detecting:
            if time.time() - self.detection_start_time >= 5:
                self.is_detecting = False
                self.status_var.set("Đã hoàn thành nhận diện")
                
                # Khởi tạo dictionary cho JSON
                keypoints_data = {
                    "docAm": {"xLeft": 0, "yLeft": 0, "xRight": 0, "yRight": 0},
                    "lyNoiDinh": {"xLeft": 0, "yLeft": 0, "xRight": 0, "yRight": 0},
                    "mauChiLyHoanhVan": {"xLeft": 0, "yLeft": 0, "xRight": 0, "yRight": 0},
                    "dungTuyen": {"xLeft": 0, "yLeft": 0, "xRight": 0, "yRight": 0},
                    "tucTam": {"xLeft": 0, "yLeft": 0, "xRight": 0, "yRight": 0},
                    "thatMien": {"xLeft": 0, "yLeft": 0, "xRight": 0, "yRight": 0}
                }

                # Xử lý frame trái
                if self.best_frame_left is not None:
                    results = self.model(self.best_frame_left)
                    if len(results) > 0 and results[0].keypoints is not None:
                        points = results[0].keypoints[0].data[0].cpu().numpy()
                        
                        # Xử lý từng điểm riêng biệt cho chân trái
                        # Đốc âm (index 0)
                        x, y = int(points[0][0]), int(points[0][1])
                        machine_x = round((1226 - x) * (250 / 1146))
                        machine_y = round((622 - y) * (120 / 571))
                        keypoints_data["docAm"]["xLeft"] = max(0, min(250, machine_x))
                        keypoints_data["docAm"]["yLeft"] = max(0, min(120, machine_y))

                        # Lý nội đình (index 1)
                        x, y = int(points[1][0]), int(points[1][1])
                        machine_x = round((1226 - x) * (250 / 1146))
                        machine_y = round((622 - y) * (120 / 571))
                        keypoints_data["lyNoiDinh"]["xLeft"] = max(0, min(250, machine_x))
                        keypoints_data["lyNoiDinh"]["yLeft"] = max(0, min(120, machine_y))

                        # Mẫu chi lý hoành vận (index 2)
                        x, y = int(points[2][0]), int(points[2][1])
                        machine_x = round((1226 - x) * (250 / 1146))
                        machine_y = round((622 - y) * (120 / 571))
                        keypoints_data["mauChiLyHoanhVan"]["xLeft"] = max(0, min(250, machine_x))
                        keypoints_data["mauChiLyHoanhVan"]["yLeft"] = max(0, min(120, machine_y))

                        # Dũng tuyền (index 3)
                        x, y = int(points[3][0]), int(points[3][1])
                        machine_x = round((1226 - x) * (250 / 1146))
                        machine_y = round((622 - y) * (120 / 571))
                        keypoints_data["dungTuyen"]["xLeft"] = max(0, min(250, machine_x))
                        keypoints_data["dungTuyen"]["yLeft"] = max(0, min(120, machine_y))

                        # Túc tam lý (index 4)
                        x, y = int(points[4][0]), int(points[4][1])
                        machine_x = round((1226 - x) * (250 / 1146))
                        machine_y = round((622 - y) * (120 / 571))
                        keypoints_data["tucTam"]["xLeft"] = max(0, min(250, machine_x))
                        keypoints_data["tucTam"]["yLeft"] = max(0, min(120, machine_y))

                        # Thất miên (index 5)
                        x, y = int(points[5][0]), int(points[5][1])
                        machine_x = round((1226 - x) * (250 / 1146))
                        machine_y = round((622 - y) * (120 / 571))
                        keypoints_data["thatMien"]["xLeft"] = max(0, min(250, machine_x))
                        keypoints_data["thatMien"]["yLeft"] = max(0, min(120, machine_y))

                # Xử lý frame phải
                if self.best_frame_right is not None:
                    results = self.model(self.best_frame_right)
                    if len(results) > 0 and results[0].keypoints is not None:
                        points = results[0].keypoints[0].data[0].cpu().numpy()
                        
                        # Xử lý từng điểm riêng biệt cho chân phải
                        # Đốc âm (index 0)
                        x, y = int(points[0][0]), int(points[0][1])
                        machine_x = round((1226 - x) * (250 / 1146))
                        machine_y = round((622 - y) * (120 / 571))
                        keypoints_data["docAm"]["xRight"] = max(0, min(250, machine_x))
                        keypoints_data["docAm"]["yRight"] = max(0, min(120, machine_y))

                        # Lý nội đình (index 1)
                        x, y = int(points[1][0]), int(points[1][1])
                        machine_x = round((1226 - x) * (250 / 1146))
                        machine_y = round((622 - y) * (120 / 571))
                        keypoints_data["lyNoiDinh"]["xRight"] = max(0, min(250, machine_x))
                        keypoints_data["lyNoiDinh"]["yRight"] = max(0, min(120, machine_y))

                        # Mẫu chi lý hoành vận (index 2)
                        x, y = int(points[2][0]), int(points[2][1])
                        machine_x = round((1226 - x) * (250 / 1146))
                        machine_y = round((622 - y) * (120 / 571))
                        keypoints_data["mauChiLyHoanhVan"]["xRight"] = max(0, min(250, machine_x))
                        keypoints_data["mauChiLyHoanhVan"]["yRight"] = max(0, min(120, machine_y))

                        # Dũng tuyền (index 3)
                        x, y = int(points[3][0]), int(points[3][1])
                        machine_x = round((1226 - x) * (250 / 1146))
                        machine_y = round((622 - y) * (120 / 571))
                        keypoints_data["dungTuyen"]["xRight"] = max(0, min(250, machine_x))
                        keypoints_data["dungTuyen"]["yRight"] = max(0, min(120, machine_y))

                        # Túc tam lý (index 4)
                        x, y = int(points[4][0]), int(points[4][1])
                        machine_x = round((1226 - x) * (250 / 1146))
                        machine_y = round((622 - y) * (120 / 571))
                        keypoints_data["tucTam"]["xRight"] = max(0, min(250, machine_x))
                        keypoints_data["tucTam"]["yRight"] = max(0, min(120, machine_y))

                        # Thất miên (index 5)
                        x, y = int(points[5][0]), int(points[5][1])
                        machine_x = round((1226 - x) * (250 / 1146))
                        machine_y = round((622 - y) * (120 / 571))
                        keypoints_data["thatMien"]["xRight"] = max(0, min(250, machine_x))
                        keypoints_data["thatMien"]["yRight"] = max(0, min(120, machine_y))

                # Thêm bài bấm huyệt được chọn vào keypoints_data
                selected_treatment = self.treatment_var.get()
                keypoints_data["baiBamHuyet"] = int(selected_treatment)

                # Tạo chuỗi JSON và gửi đi
                json_string = json.dumps(keypoints_data, indent=2)
                final_string = f"*\n{json_string}\n#\n"
                print(final_string)
                
                if self.uart.is_connected:
                    if self.uart.send_data(final_string):
                        self.status_var.set("Đã gửi dữ liệu thành công")
                    else:
                        self.status_var.set("Lỗi khi gửi dữ liệu UART")
                else:
                    print("Không thể gửi dữ liệu: UART chưa được kết nối")
                break

            ret_left, frame_left = self.cap_left.read()
            ret_right, frame_right = self.cap_right.read()

            if ret_left and ret_right:
                # Nhận diện với YOLO-pose
                results_left = self.model(frame_left)
                results_right = self.model(frame_right)

                # Xử lý và hiển thị keypoints cho camera bên trái
                annotated_frame_left = results_left[0].plot(
                    kpt_radius=12
                )
                self.best_frame_left = annotated_frame_left

                # Xử lý và hiển thị keypoints cho camera bên phải
                annotated_frame_right = results_right[0].plot(
                    kpt_radius=12
                )
                self.best_frame_right = annotated_frame_right
    
    def print_keypoints(self, frame):
        """
        In ra tất cả các tọa độ keypoints từ frame
        """
        keypoint_names = {
            0: "Hoanh-Van",
            1: "Noi-Dinh",
            2: "Doc-Am",
            3: "Dung-Tuyen",
            4: "Tuc-Tam",
            5: "That-Mien"
        }
        results = self.model(frame)
        
        for r in results:
            if r.keypoints is not None:
                keypoints = r.keypoints.xy.cpu().numpy()[0]
                print("\nTọa độ các điểm:")
                for i, point in enumerate(keypoints):
                    point_name = keypoint_names.get(i, f"Điểm {i}")
                    print(f"{point_name}: (x: {point[0]:.2f}, y: {point[1]:.2f})")
    
    def draw_machine_grid(self, frame, is_right_foot=False):
        """
        Vẽ lưới tọa độ máy với khoảng cách 10mm
        Gốc tọa độ (0,0):
        - Chân trái: góc phải trên, X tăng từ phải sang trái
        - Chân phải: góc phải dưới, X tăng từ phải sang trái
        """
        # Tọa độ crop và kích thước
        x_start = 80  # Điểm bắt đầu X (trái)
        y_start = 51  # Điểm bắt đầu Y (trên)
        x_end = 1226  # Điểm kết thúc X (phải)
        y_end = 622   # Điểm kết thúc Y (dưới)

        # Vẽ khung viền khu vực
        cv2.rectangle(frame,
                     (x_start, y_start),
                     (x_end, y_end),
                     (0, 255, 0), 2)

        width = x_end - x_start   # = 1146 pixels
        height = y_end - y_start  # = 571 pixels

        x_step = width / 25   # Chia 250mm thành 25 phần (mỗi 10mm)
        y_step = height / 12  # Chia 120mm thành 12 phần (mỗi 10mm)

        # Vẽ các đường dọc (theo trục x)
        for i in range(26):  # 0 đến 250mm, mỗi 10mm
            if is_right_foot:
                # Chân phải: X tính từ phải sang trái
                x = int(x_end - i * x_step)
            else:
                # Chân trái: X tính từ phải sang trái
                x = int(x_end - i * x_step) # Giữ nguyên cách tính X

            cv2.line(frame,
                    (x, y_start),
                    (x, y_end),
                    (0, 255, 0), 1)

            # Hiển thị số tọa độ x (mỗi 50mm)
            if i % 5 == 0:
                cv2.putText(frame, str(i * 10),
                          (x - 10, y_start - 10), # Thay đổi vị trí Y
                          cv2.FONT_HERSHEY_SIMPLEX,
                          0.5, (0, 255, 0), 1)

        # Vẽ các đường ngang (theo trục y)
        for i in range(13):  # 0 đến 120mm, mỗi 10mm
            y = int(y_start + i * y_step)  # Y tính từ trên xuống
            cv2.line(frame,
                    (x_start, y),
                    (x_end, y),
                    (0, 255, 0), 1)

            # Hiển thị số tọa độ y
            if i % 3 == 0:
                if is_right_foot:
                    # Chân phải: số ở bên phải
                    cv2.putText(frame, str(i * 10),
                              (x_end + 5, y + 5),
                              cv2.FONT_HERSHEY_SIMPLEX,
                              0.5, (0, 255, 0), 1)
                else:
                    # Chân trái: số ở bên phải
                    cv2.putText(frame, str(i * 10),
                              (x_end + 5, y + 5), # Thay đổi vị trí X
                              cv2.FONT_HERSHEY_SIMPLEX,
                              0.5, (0, 255, 0), 1)

        # Vẽ gốc tọa độ (0,0)
        if is_right_foot:
            # Chân phải: (0,0) ở góc phải dưới
            cv2.circle(frame, (x_end, y_end), 3, (0, 255, 0), -1)
            cv2.putText(frame, "(0,0)",
                      (x_end + 5, y_end + 15),
                      cv2.FONT_HERSHEY_SIMPLEX,
                      0.5, (0, 255, 0), 1)
        else:
            # Chân trái: (0,0) ở góc phải trên
            cv2.circle(frame, (x_end, y_start), 3, (0, 255, 0), -1)
            cv2.putText(frame, "(0,0)",
                      (x_end + 5, y_start - 15),
                      cv2.FONT_HERSHEY_SIMPLEX,
                      0.5, (0, 255, 0), 1)

        return frame

    def get_machine_coordinates(self, pixel_x, pixel_y, is_right_foot=False):
        """
        Chuyển đổi tọa độ pixel sang tọa độ máy dựa trên lưới
        """
        # Tọa độ crop và kích thước
        x_start = 80
        x_end = 1226
        y_start = 51
        y_end = 622
        crop_width = x_end - x_start
        crop_height = y_end - y_start

        # Kiểm tra điểm có nằm trong vùng crop
        if (pixel_x < x_start or pixel_x > x_end or
            pixel_y < y_start or pixel_y > y_end):
            return None

        if is_right_foot:
            # Chân phải: X tính từ phải sang trái
            machine_x = int(round((x_end - pixel_x) * 250 / crop_width))
        else:
            # Chân trái: X tính từ phải sang trái
            machine_x = int(round((x_end - pixel_x) * 250 / crop_width)) # X tính từ phải sang trái

        # Y tính từ trên xuống
        machine_y = int(round((pixel_y - y_start) * 120 / crop_height))

        return machine_x, machine_y

    def process_keypoints(self, frame, side):
        """
        Xử lý và hiển thị keypoints từ YOLO
        Gốc tọa độ (0,0):
        - Chân trái: góc trái dưới, X tăng từ trái sang phải
        - Chân phải: góc phải dưới, X tăng từ phải sang trái
        """
        results = self.model(frame)
        
        if len(results) > 0:
            result = results[0]
            if result.keypoints is not None:
                keypoints = result.keypoints[0]
                points = keypoints.data[0].cpu().numpy()
                confidences = keypoints.conf[0].cpu().numpy()

                # Map tên huyệt
                huyet_map = {
                    0: "mauChiLyHoanhVan",
                    1: "lyNoiDinh",
                    2: "docAm",
                    3: "dungTuyen",
                    4: "tucTam",
                    5: "thatMien"
                }

                for idx, (point, conf) in enumerate(zip(points, confidences)):
                    if conf > 0.5 and idx in huyet_map:
                        x, y = int(point[0]), int(point[1])
                        
                        if side == "right":
                            # Chân phải: X tính từ phải sang trái
                            machine_y = round((1226 - x) * (250 / 1146))
                            # Y tính từ trên xuống
                            machine_x = round((y - 51) * (120 / 571))
                        else:
                            # Chân trái: X tính từ phải sang trái (đảo ngược)
                            machine_y = round((1226 - x) * (250 / 1146))
                            # Y tính từ trên xuống
                            machine_x = round((y - 51) * (120 / 571))
                        
                        # Giới hạn tọa độ
                        machine_x = max(0, min(250, machine_x))
                        machine_y = max(0, min(120, machine_y))

                        # Vẽ điểm YOLO
                        cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
                        
                        # Hiển thị tên huyệt và tọa độ máy
                        text = f"{huyet_map[idx]}: M({machine_x},{machine_y})"
                        cv2.putText(frame, text,
                                  (x + 10, y - 10),
                                  cv2.FONT_HERSHEY_SIMPLEX,
                                  0.5, (0, 255, 255), 1)

        return frame

    def display_coordinates(self, frame, yolo_coords, machine_coords, huyet_name, side):
        """
        Hiển thị tọa độ YOLO và tọa độ máy lên frame
        """
        # Tọa độ YOLO (pixel)
        yolo_x, yolo_y = int(yolo_coords[0]), int(yolo_coords[1])
        
        # Tọa độ máy
        machine_x, machine_y = machine_coords
        
        # Vẽ điểm và hiển thị thông tin
        cv2.circle(frame, (yolo_x, yolo_y), 5, (0, 255, 0), -1)  # Vẽ điểm màu xanh lá
        text = f"{huyet_name}_{side}: YOLO({yolo_x},{yolo_y}) -> Machine({machine_x},{machine_y})"
        cv2.putText(frame, text, (yolo_x + 10, yolo_y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    def print_and_store_keypoints(self, frame, side):
        """
        In ra thông tin keypoints và lưu vào dict
        """
        results = self.model(frame)

        # Danh sách tên huyệt (cần điều chỉnh nếu cần)
        huyet_names = ["huyet1", "huyet2", "huyet3", "huyet4", "huyet5", "huyet6"]
        # Huyệt tương ứng với các keypoints
        huyet_keypoints_mapping = {
            "left": {
                "mauChiLyHoanhVan_left": [6, 8],  # Ví dụ keypoints 6 và 8 cho huyệt 1 bên trái
                "lyNoiDinh_left": [6, 8],
                "docAm_left": [6, 8],
                "dungTuyen_left": [14, 16],
                "tucTam_left": [14, 16],
                "thatMien_left": [14, 16]
            },
            "right": {
                "mauChiLyHoanhVan_right": [5, 7],  # Ví dụ keypoints 5 và 7 cho huyệt 1 bên phải
                "lyNoiDinh_right": [5, 7],
                "docAm_right": [5, 7],
                "dungTuyen_right": [13, 15],
                "tucTam_right": [13, 15],
                "thatMien_right": [13, 15]
            }
        }

        for r in results:
            if r.keypoints is not None:
                keypoints = r.keypoints.xy.cpu().numpy()[0]  # Lấy keypoints từ kết quả

                for huyet_name, kp_indices in huyet_keypoints_mapping[side].items():
                    x_coords = []
                    y_coords = []
                    for index in kp_indices:
                        if index < len(keypoints):
                            x_coords.append(int(keypoints[index][0]))
                            y_coords.append(int(keypoints[index][1]))
                            print(f"  Keypoint {index}: (x: {keypoints[index][0]:.2f}, y: {keypoints[index][1]:.2f})")

                    if len(x_coords) == 2 and len(y_coords) == 2:
                        self.keypoints_data[huyet_name] = {
                            "xLeft": x_coords[0],
                            "yLeft": 120 - y_coords[0],
                            "xRight": x_coords[1],
                            "yRight": 120 - y_coords[1]
                        }
                        print(f"Huyet {huyet_name} ({side}):")
                        print(f"  xLeft: {x_coords[0]}, yLeft: {120 - y_coords[0]}")
                        print(f"  xRight: {x_coords[1]}, yRight: {120 - y_coords[1]}")

    def print_json_string(self):
        """
        Tạo và in chuỗi JSON
        """
        # Thêm bài bấm huyệt vào dict
        selected_treatment = self.treatment_combo.get()
        treatment_mapping = {
            "Sốt, co giật": 1,
            "Stress": 2,
            "Thoát vị đĩa đệm": 3,
            "Bổ thận tráng dương": 4,
            "Nâng cao sức khỏe": 5
        }
        bai_bam_huyet = treatment_mapping.get(selected_treatment, 1)
        self.keypoints_data["baiBamHuyet"] = bai_bam_huyet

        # Tạo chuỗi JSON
        json_string = json.dumps(self.keypoints_data, indent=2)

        # In chuỗi JSON ra terminal
        print("\nChuỗi JSON gửi đi:")
        print(f"*\n {json_string} #\n")

    def update_frames(self):
        if not self.is_detecting:
            if self.best_frame_left is not None and self.best_frame_right is not None:
                self.show_frame(self.best_frame_left, self.canvas_left)
                self.show_frame(self.best_frame_right, self.canvas_right)
            else:
                ret_left, frame_left = self.cap_left.read()
                ret_right, frame_right = self.cap_right.read()

                if ret_left and ret_right:
                    self.show_frame(frame_left, self.canvas_left)
                    self.show_frame(frame_right, self.canvas_right)

        self.window.after(10, self.update_frames)

    def show_frame(self, frame, canvas):
        """Hiển thị frame lên canvas"""
        if frame is not None:
            # Vẽ lưới với tham số is_right_foot tùy theo canvas
            frame = self.draw_machine_grid(
                frame.copy(), 
                is_right_foot=(canvas == self.canvas_right)
            )
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Xoay frame 90 độ ngay tại đây khi hiển thị
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

            # Chuyển đổi màu từ BGR sang RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            frame = cv2.flip(frame, 1)

            # Cập nhật kích thước canvas
            canvas.update_idletasks()
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()

            if canvas_width > 1 and canvas_height > 1:
                # Tính toán resize giữ nguyên tỷ lệ khung hình
                frame_height, frame_width = frame.shape[:2]
                scale = min(canvas_width / frame_width, canvas_height / frame_height)

                new_width = int(frame_width * scale)
                new_height = int(frame_height * scale)

                # Resize ảnh với phương pháp interpolation tốt hơn
                frame_resized = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

                # Chuyển đổi sang ảnh PhotoImage
                photo = ImageTk.PhotoImage(image=Image.fromarray(frame_resized))

                # Xoá canvas cũ và vẽ ảnh mới căn giữa
                canvas.delete("all")
                canvas.create_image(
                    canvas_width / 2,
                    canvas_height / 2,
                    image=photo,
                    anchor=tk.CENTER
                )

                # Giữ tham chiếu ảnh để tránh bị thu dọn bởi garbage collector
                canvas.photo = photo

    def on_closing(self):
        """Đóng ứng dụng và dọn dẹp"""
        self.is_detecting = False
        if hasattr(self, 'uart'):
            self.uart.close()
        if self.cap_left.isOpened():
            self.cap_left.release()
        if self.cap_right.isOpened():
            self.cap_right.release()
        self.window.destroy()

    def start_pressing(self):
        """Gửi lệnh bắt đầu bấm huyệt"""
        self.status_var.set("Bắt đầu bấm huyệt...")
        if self.uart.is_connected:
            self.uart.send_data("*\n Start #\n")
        else:
            print("Không thể gửi lệnh: UART chưa được kết nối")

    def stop_machine(self):
        """Gửi lệnh dừng máy"""
        self.status_var.set("Máy đã dừng.")
        if self.uart.is_connected:
            self.uart.send_data("*\n Stop #\n")
        else:
            print("Không thể gửi lệnh: UART chưa được kết nối")

    def start_medicine(self):
        self.status_var.set("Bật dẫn dược.")

    def stop_medicine(self):
        self.status_var.set("Tắt dẫn dược.")

    def burn_medicine(self):
        self.status_var.set("Đang đốt dược liệu...")

    def stop_burn_medicine(self):
        self.status_var.set("Tắt đốt dược liệu.")

    def get_keypoints_json(self):
        """
        Lấy thông tin các huyệt theo tọa độ máy và trả về dạng JSON
        Format:
        {
            "mauChiLyHoanhVan": {"xLeft": val, "yLeft": val, "xRight": val, "yRight": val},
            "lyNoiDinh": {"xLeft": val, "yLeft": val, "xRight": val, "yRight": val},
            ...
        }
        """
        # Khởi tạo dictionary cho JSON
        keypoints_data = {
            "mauChiLyHoanhVan": {"xLeft": None, "yLeft": None, "xRight": None, "yRight": None},
            "lyNoiDinh": {"xLeft": None, "yLeft": None, "xRight": None, "yRight": None},
            "docAm": {"xLeft": None, "yLeft": None, "xRight": None, "yRight": None},
            "dungTuyen": {"xLeft": None, "yLeft": None, "xRight": None, "yRight": None},
            "tucTam": {"xLeft": None, "yLeft": None, "xRight": None, "yRight": None},
            "thatMien_left": {"xLeft": None, "yLeft": None, "xRight": None, "yRight": None}
        }

        # Hàm helper để tính tọa độ máy
        def calculate_machine_coords(x, y, is_right_foot):
            # Kích thước vùng crop (pixel)
            crop_width = 1146  # 1226 - 80
            crop_height = 571  # 622 - 51
            
            # Kích thước thực tế của máy (mm)
            machine_width = 250  # mm
            machine_height = 120  # mm
            
            # Tính tỷ lệ chuyển đổi
            x_scale = machine_width / crop_width
            y_scale = machine_height / crop_height
            
            # Tính toán tọa độ máy
            if is_right_foot:
                # Chân phải: X tính từ phải sang trái
                machine_x = round((1226 - x) * x_scale)
            else:
                # Chân trái: X tính từ trái sang phải
                machine_x = round((x - 80) * x_scale)
            
            # Y luôn tính từ dưới lên trên
            machine_y = round((622 - y) * y_scale)
            
            # Giới hạn tọa độ trong phạm vi máy
            machine_x = max(0, min(machine_width, machine_x))
            machine_y = max(0, min(machine_height, machine_y))
            
            return machine_x, machine_y

        # Xử lý frame trái
        if self.best_frame_left is not None:
            results = self.model(self.best_frame_left)
            if len(results) > 0 and results[0].keypoints is not None:
                keypoints = results[0].keypoints[0]
                points = keypoints.data[0].cpu().numpy()
                confidences = keypoints.conf[0].cpu().numpy()

                # Chỉ xử lý các điểm có độ tin cậy > 0.5
                for idx, (point, conf) in enumerate(zip(points, confidences)):
                    if conf > 0.5:
                        x, y = int(point[0]), int(point[1])
                        machine_x, machine_y = calculate_machine_coords(x, y, False)

                        # Gán tọa độ vào JSON theo index
                        point_map = {
                            0: "mauChiLyHoanhVan",
                            1: "lyNoiDinh",
                            2: "docAm",
                            3: "dungTuyen",
                            4: "tucTam",
                            5: "thatMien_left"
                        }

                        if idx in point_map:
                            keypoints_data[point_map[idx]]["xLeft"] = machine_x
                            keypoints_data[point_map[idx]]["yLeft"] = machine_y

        # Xử lý frame phải
        if self.best_frame_right is not None:
            results = self.model(self.best_frame_right)
            if len(results) > 0 and results[0].keypoints is not None:
                keypoints = results[0].keypoints[0]
                points = keypoints.data[0].cpu().numpy()
                confidences = keypoints.conf[0].cpu().numpy()

                # Chỉ xử lý các điểm có độ tin cậy > 0.5
                for idx, (point, conf) in enumerate(zip(points, confidences)):
                    if conf > 0.5:
                        x, y = int(point[0]), int(point[1])
                        machine_x, machine_y = calculate_machine_coords(x, y, True)

                        # Gán tọa độ vào JSON theo index
                        point_map = {
                            0: "mauChiLyHoanhVan",
                            1: "lyNoiDinh",
                            2: "docAm",
                            3: "dungTuyen",
                            4: "tucTam",
                            5: "thatMien_left"
                        }

                        if idx in point_map:
                            keypoints_data[point_map[idx]]["xRight"] = machine_x
                            keypoints_data[point_map[idx]]["yRight"] = machine_y

        # Chuyển None thành 0 trong JSON
        for huyet in keypoints_data:
            for coord in keypoints_data[huyet]:
                if keypoints_data[huyet][coord] is None:
                    keypoints_data[huyet][coord] = 0

        return json.dumps(keypoints_data, indent=2)

    def get_uart_string(self):
        """
        Tạo chuỗi UART từ tọa độ máy theo format:
        "mauChiLyHoanhVan,xLeft,yLeft,xRight,yRight;lyNoiDinh,xLeft,yLeft,xRight,yRight;..."
        """
        # Khởi tạo danh sách các huyệt theo thứ tự
        huyet_points = [
            "mauChiLyHoanhVan",
            "lyNoiDinh", 
            "docAm",
            "dungTuyen",
            "tucTam",
            "thatMien_left"
        ]
        
        # Tính toán tọa độ máy cho từng điểm
        coords = {huyet: {"xLeft": 0, "yLeft": 0, "xRight": 0, "yRight": 0} for huyet in huyet_points}
        
        # Hàm helper để tính tọa độ máy
        def calculate_machine_coords(x, y, is_right_foot):
            x_start = 80
            x_end = 1226
            y_start = 51
            y_end = 622
            crop_width = x_end - x_start
            crop_height = y_end - y_start
            x_scale = 250 / crop_width
            y_scale = 120 / crop_height

            if is_right_foot:
                # Chân phải: X tính từ phải sang trái
                machine_x = round((x_end - x) * x_scale)
            else:
                # Chân trái: X tính từ trái sang phải
                machine_x = round((x - x_start) * x_scale)

            # Y tính từ dưới lên trên
            machine_y = round((y_end - y) * y_scale)

            # Giới hạn tọa độ
            machine_x = max(0, min(250, machine_x))
            machine_y = max(0, min(120, machine_y))

            return machine_x, machine_y

        # Xử lý frame trái
        if self.best_frame_left is not None:
            results = self.model(self.best_frame_left)
            if len(results) > 0 and results[0].keypoints is not None:
                keypoints = results[0].keypoints[0]
                points = keypoints.data[0].cpu().numpy()
                confidences = keypoints.conf[0].cpu().numpy()

                for idx, (point, conf) in enumerate(zip(points, confidences)):
                    if conf > 0.5 and idx < len(huyet_points):
                        x, y = int(point[0]), int(point[1])
                        machine_x, machine_y = calculate_machine_coords(x, y, False)
                        coords[huyet_points[idx]]["xLeft"] = machine_x
                        coords[huyet_points[idx]]["yLeft"] = machine_y

        # Xử lý frame phải
        if self.best_frame_right is not None:
            results = self.model(self.best_frame_right)
            if len(results) > 0 and results[0].keypoints is not None:
                keypoints = results[0].keypoints[0]
                points = keypoints.data[0].cpu().numpy()
                confidences = keypoints.conf[0].cpu().numpy()

                for idx, (point, conf) in enumerate(zip(points, confidences)):
                    if conf > 0.5 and idx < len(huyet_points):
                        x, y = int(point[0]), int(point[1])
                        machine_x, machine_y = calculate_machine_coords(x, y, True)
                        coords[huyet_points[idx]]["xRight"] = machine_x
                        coords[huyet_points[idx]]["yRight"] = machine_y

        # Tạo chuỗi UART
        uart_parts = []
        for huyet in huyet_points:
            c = coords[huyet]
            uart_parts.append(f"{huyet},{c['xLeft']},{c['yLeft']},{c['xRight']},{c['yRight']}")
        
        uart_string = ";".join(uart_parts)
        return uart_string
    

if __name__ == "__main__":
    root = tk.Tk()
    app = MedicalControlApp(root, "BMD Machine Control V3.5")
    root.mainloop()