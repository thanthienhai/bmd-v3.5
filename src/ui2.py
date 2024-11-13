import tkinter as tk
from tkinter import ttk
import cv2
import torch
from ultralytics import YOLO
import time
from PIL import Image, ImageTk
import threading
import numpy as np

class MedicalControlApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        
        # Kích hoạt chế độ toàn màn hình
        self.window.attributes("-fullscreen", True)
        
        # Bind phím Esc để thoát khỏi toàn màn hình
        self.window.bind("<Escape>", self.toggle_fullscreen)
        
        # Áp dụng theme
        style = ttk.Style()
        style.theme_use('clam')  # Bạn có thể thay đổi theme tùy ý

        # Định nghĩa style cho các nút
        style.configure("TButton", font=("Arial", 14), padding=2)  # Giảm padding
        style.map("OnButton.TButton",
                  foreground=[('pressed', 'white'), ('active', 'white')],
                  background=[('pressed', 'green'), ('active', 'green')])
        style.map("OffButton.TButton",
                  foreground=[('pressed', 'white'), ('active', 'white')],
                  background=[('pressed', 'red'), ('active', 'red')])

        # Định nghĩa style cho Combobox lớn hơn
        self.combo_font = ("Arial", 16)  # Tăng kích thước phông chữ
        style.configure("Large.TCombobox", font=self.combo_font)

        # Khởi tạo model YOLO
        self.model = YOLO('/home/thanthien/Coding/bmd-v3.5/models/best-640-100eps.pt')

        # Khởi tạo camera
        self.cap_left = cv2.VideoCapture('/home/thanthien/Coding/bmd-v3.5/video_test/1.mp4')
        self.cap_right = cv2.VideoCapture('/home/thanthien/Coding/bmd-v3.5/video_test/2.mp4')

        # Biến lưu frame tốt nhất
        self.best_frame_left = None
        self.best_frame_right = None
        self.best_conf_left = 0
        self.best_conf_right = 0

        # Biến điều khiển
        self.is_detecting = False
        self.detection_start_time = 0

        # Tạo giao diện
        self.create_gui()

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        is_fullscreen = self.window.attributes("-fullscreen")
        self.window.attributes("-fullscreen", not is_fullscreen)

    def create_gui(self):
        # Frame chính
        main_frame = ttk.Frame(self.window, padding=2)  # Giảm padding
        main_frame.grid(row=0, column=0, sticky="NSEW")

        # Cấu trúc grid cho main_frame
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)

        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)

        # Frame hiển thị camera
        camera_frame = ttk.LabelFrame(main_frame, text="Hiển thị camera", padding=2)  # Giảm padding
        camera_frame.grid(row=0, column=0, sticky="NSEW", padx=(0, 10), pady=5)  # Giảm padx và pady

        # Cấu trúc grid cho camera_frame
        camera_frame.columnconfigure(0, weight=1)
        camera_frame.columnconfigure(1, weight=1)
        camera_frame.rowconfigure(0, weight=1)

        # Frame cho camera trái
        left_camera_frame = ttk.LabelFrame(camera_frame, text="Chân trái", padding=2)  # Giảm padding
        left_camera_frame.grid(row=0, column=0, sticky="NSEW", padx=5, pady=5)  # Giảm padx và pady
        self.canvas_left = tk.Canvas(left_camera_frame, bg="black")
        self.canvas_left.pack(expand=True, fill='both')

        # Frame cho camera phải
        right_camera_frame = ttk.LabelFrame(camera_frame, text="Chân phải", padding=2)  # Giảm padding
        right_camera_frame.grid(row=0, column=1, sticky="NSEW", padx=5, pady=5)  # Giảm padx và pady
        self.canvas_right = tk.Canvas(right_camera_frame, bg="black")
        self.canvas_right.pack(expand=True, fill='both')

        # Frame điều khiển
        control_frame = ttk.LabelFrame(main_frame, text="Điều khiển", padding=2)  # Giảm padding
        control_frame.grid(row=0, column=1, sticky="NSEW", pady=5)  # Giảm pady

        # Cấu trúc grid cho control_frame
        control_frame.columnconfigure(0, weight=1)

        # Chọn bài bấm huyệt
        treatment_label = ttk.Label(control_frame, text="Chọn bài bấm huyệt:", font=("Arial", 16))  # Giảm kích thước font
        treatment_label.grid(row=0, column=0, sticky="W", pady=(0, 5))  # Giảm pady

        self.treatment_combo = ttk.Combobox(control_frame, state="readonly", values=(
            "Sốt, co giật",
            "Stress",
            "Thoát vị đĩa đệm",
            "Bổ thận tráng dương",
            "Nâng cao sức khỏe"
        ), style="Large.TCombobox", width=30)  # Giữ width
        self.treatment_combo.grid(row=1, column=0, sticky="EW", pady=(0, 10), ipadx=5, ipady=5)  # Giảm pady và ipadx/ipady
        self.treatment_combo.set("Chọn bài bấm huyệt")

        # Frame cho các nút điều khiển chính
        main_buttons_frame = ttk.LabelFrame(control_frame, text="Điều khiển chính", padding=2)  # Giảm padding
        main_buttons_frame.grid(row=2, column=0, sticky="EW", pady=5)  # Giảm pady

        # Sắp xếp các nút điều khiển chính ngang hàng với rộng hơn và padding
        detect_button = ttk.Button(
            main_buttons_frame,
            text="Nhận diện huyệt",
            command=self.start_detection
        )
        detect_button.grid(row=0, column=0, padx=5, pady=5, sticky="EW", ipadx=5)  # Giảm padx, pady, ipadx

        start_press_button = ttk.Button(
            main_buttons_frame,
            text="Bắt đầu bấm huyệt",
            command=self.start_pressing  # Bạn cần định nghĩa hàm này
        )
        start_press_button.grid(row=0, column=1, padx=5, pady=5, sticky="EW", ipadx=5)  # Giảm padx, pady, ipadx

        stop_button = ttk.Button(
            main_buttons_frame,
            text="Dừng máy",
            command=self.stop_machine  # Bạn cần định nghĩa hàm này
        )
        stop_button.grid(row=0, column=2, padx=5, pady=5, sticky="EW", ipadx=5)  # Giảm padx, pady, ipadx

        main_buttons_frame.columnconfigure(0, weight=1)
        main_buttons_frame.columnconfigure(1, weight=1)
        main_buttons_frame.columnconfigure(2, weight=1)

        # Frame cho điều khiển dẫn dược
        medicine_frame = ttk.LabelFrame(control_frame, text="Điều khiển dẫn dược", padding=2)  # Giảm padding
        medicine_frame.grid(row=3, column=0, sticky="EW", pady=5)  # Giảm pady

        # Sắp xếp các nút điều khiển dẫn dược ngang hàng với rộng hơn và padding
        start_medicine_button = ttk.Button(
            medicine_frame,
            text="Bật dẫn dược",
            style="OnButton.TButton",
            command=self.start_medicine  # Bạn cần định nghĩa hàm này
        )
        start_medicine_button.grid(row=0, column=0, padx=5, pady=5, sticky="EW", ipadx=5)  # Giảm padx, pady, ipadx

        stop_medicine_button = ttk.Button(
            medicine_frame,
            text="Tắt dẫn dược",
            style="OffButton.TButton",
            command=self.stop_medicine  # Bạn cần định nghĩa hàm này
        )
        stop_medicine_button.grid(row=0, column=1, padx=5, pady=5, sticky="EW", ipadx=5)  # Giảm padx, pady, ipadx

        medicine_frame.columnconfigure(0, weight=1)
        medicine_frame.columnconfigure(1, weight=1)

        # Frame cho điều khiển đốt dược liệu
        burning_frame = ttk.LabelFrame(control_frame, text="Điều khiển đốt dược liệu", padding=2)  # Giảm padding
        burning_frame.grid(row=4, column=0, sticky="EW", pady=5)  # Giảm pady

        # Sắp xếp các nút điều khiển đốt dược liệu ngang hàng với rộng hơn và padding
        burn_button = ttk.Button(
            burning_frame,
            text="Đốt dược liệu",
            style="OnButton.TButton",
            command=self.burn_medicine  # Bạn cần định nghĩa hàm này
        )
        burn_button.grid(row=0, column=0, padx=5, pady=5, sticky="EW", ipadx=5)  # Giảm padx, pady, ipadx

        stop_burn_button = ttk.Button(
            burning_frame,
            text="Tắt đốt dược liệu",
            style="OffButton.TButton",
            command=self.stop_burn_medicine  # Bạn cần định nghĩa hàm này
        )
        stop_burn_button.grid(row=0, column=1, padx=5, pady=5, sticky="EW", ipadx=5)  # Giảm padx, pady, ipadx

        burning_frame.columnconfigure(0, weight=1)
        burning_frame.columnconfigure(1, weight=1)

        # Nút thoát
        exit_button = ttk.Button(
            control_frame,
            text="THOÁT",
            command=self.on_closing
        )
        exit_button.grid(row=5, column=0, sticky="EW", pady=15, ipadx=5)  # Giảm pady, ipadx

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Sẵn sàng")
        status_bar = ttk.Label(
            self.window,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=2  # Giảm padding
        )
        status_bar.grid(row=1, column=0, sticky="EW")

        # Update frames
        self.update_frames()

    def rotate_frame(self, frame):
        """Xoay frame 90 độ"""
        return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

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
                break

            ret_left, frame_left = self.cap_left.read()
            ret_right, frame_right = self.cap_right.read()

            if ret_left and ret_right:
                # Thực hiện nhận diện trước khi xoay frame
                results_left = self.model(frame_left)
                results_right = self.model(frame_right)

                # Xử lý kết quả camera trái
                if len(results_left) > 0:
                    boxes_left = results_left[0].boxes
                    conf_left = boxes_left.conf.cpu().numpy()
                    if len(conf_left) > 0:
                        # Lọc những object có độ tin cậy lớn hơn 0.8
                        valid_boxes_left = [box for box, conf in zip(boxes_left, conf_left) if conf > 0.8]
                        if valid_boxes_left:
                            # Lấy frame với các object đã lọc
                            annotated_frame_left = results_left[0].plot()
                            self.best_frame_left = annotated_frame_left
                            self.best_conf_left = max(conf_left)

                # Xử lý kết quả camera phải
                if len(results_right) > 0:
                    boxes_right = results_right[0].boxes
                    conf_right = boxes_right.conf.cpu().numpy()
                    if len(conf_right) > 0:
                        # Lọc những object có độ tin cậy lớn hơn 0.8
                        valid_boxes_right = [box for box, conf in zip(boxes_right, conf_right) if conf > 0.8]
                        if valid_boxes_right:
                            # Lấy frame với các object đã lọc
                            annotated_frame_right = results_right[0].plot()
                            self.best_frame_right = annotated_frame_right
                            self.best_conf_right = max(conf_right)

                # Xoay frame sau khi nhận diện
                frame_left = self.rotate_frame(frame_left)
                frame_right = self.rotate_frame(frame_right)


    def update_frames(self):
        if not self.is_detecting:
            if self.best_frame_left is not None and self.best_frame_right is not None:
                # Hiển thị frame có confident cao nhất
                self.show_frame(self.best_frame_left, self.canvas_left)
                self.show_frame(self.best_frame_right, self.canvas_right)
            else:
                # Hiển thị frame thông thường
                ret_left, frame_left = self.cap_left.read()
                ret_right, frame_right = self.cap_right.read()

                if ret_left and ret_right:
                    # Xoay frame
                    frame_left = self.rotate_frame(frame_left)
                    frame_right = self.rotate_frame(frame_right)

                    self.show_frame(frame_left, self.canvas_left)
                    self.show_frame(frame_right, self.canvas_right)

        self.window.after(10, self.update_frames)

    def show_frame(self, frame, canvas):
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Lấy kích thước hiện tại của canvas để điều chỉnh kích thước frame
            canvas.update_idletasks()
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            if canvas_width > 1 and canvas_height > 1:
                frame = cv2.resize(frame, (canvas_width, canvas_height))
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            canvas.photo = photo  # Giữ tham chiếu để tránh garbage collection

    def on_closing(self):
        self.is_detecting = False
        if self.cap_left.isOpened():
            self.cap_left.release()
        if self.cap_right.isOpened():
            self.cap_right.release()
        self.window.destroy()

    # Các hàm điều khiển khác (Cần định nghĩa)
    def start_pressing(self):
        # Thêm logic cho việc bắt đầu bấm huyệt
        self.status_var.set("Bắt đầu bấm huyệt...")

    def stop_machine(self):
        # Thêm logic cho việc dừng máy
        self.status_var.set("Máy đã dừng.")

    def start_medicine(self):
        # Thêm logic cho việc bật dẫn dược
        self.status_var.set("Bật dẫn dược.")

    def stop_medicine(self):
        # Thêm logic cho việc tắt dẫn dược
        self.status_var.set("Tắt dẫn dược.")

    def burn_medicine(self):
        # Thêm logic cho việc đốt dược liệu
        self.status_var.set("Đang đốt dược liệu...")

    def stop_burn_medicine(self):
        # Thêm logic cho việc tắt đốt dược liệu
        self.status_var.set("Tắt đốt dược liệu.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MedicalControlApp(root, "BMD Machine Control V3.5")
    root.mainloop()
