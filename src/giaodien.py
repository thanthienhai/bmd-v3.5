import tkinter as tk
from tkinter import ttk
import cv2
import torch
from ultralytics import YOLO
import time
from PIL import Image, ImageTk
import threading
import numpy as np
import json

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
        self.model = YOLO('/home/ubuntu/Coding/swork/bmd-v3.5/models/best-640-100eps.pt')
        self.model.conf = 0.5

        self.cap_left = cv2.VideoCapture('/home/ubuntu/Coding/swork/bmd-v3.5/video_test/1.mp4')
        self.cap_right = cv2.VideoCapture('/home/ubuntu/Coding/swork/bmd-v3.5/video_test/2.mp4')

        self.best_frame_left = None
        self.best_frame_right = None
        self.best_conf_left = 0
        self.best_conf_right = 0

        self.is_detecting = False
        self.detection_start_time = 0

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

        self.treatment_combo = ttk.Combobox(
            control_frame,
            state="readonly",
            values=[
                "Sốt, co giật",
                "Stress",
                "Thoát vị đĩa đệm",
                "Bổ thận tráng dương",
                "Nâng cao sức khỏe"
            ],
            style="Large.TCombobox",
            width=40,
            font=("Arial", 16)
        )
        self.treatment_combo.grid(
            row=1,
            column=0,
            sticky="EW",
            pady=(0, 10),
            ipadx=10,
            ipady=10
        )
        self.treatment_combo.set("Chọn bài bấm huyệt")

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
            if time.time() - self.detection_start_time >= 1:
                self.is_detecting = False
                self.status_var.set("Đã hoàn thành nhận diện")

                self.keypoints_data = {}
            
                # Xử lý frame tốt nhất của cả hai camera
                if self.best_frame_left is not None:
                    self.process_keypoints(self.best_frame_left, "left")
                if self.best_frame_right is not None:
                    self.process_keypoints(self.best_frame_right, "right")
                    
                # Thêm baiBamHuyet vào dữ liệu
                selected_treatment = self.treatment_combo.get()
                treatment_mapping = {
                    "Sốt, co giật": 1,
                    "Stress": 2,
                    "Thoát vị đĩa đệm": 3,
                    "Bổ thận tráng dương": 4,
                    "Nâng cao sức khỏe": 5
                }
                self.keypoints_data["baiBamHuyet"] = treatment_mapping.get(selected_treatment, 1)
                
                # In ra JSON
                # print("\nKết quả nhận diện:")
                # print(json.dumps(self.keypoints_data, indent=2))
                # break
                json_string = json.dumps(self.keypoints_data, indent=2)
                final_string = f"*\n {json_string} #\n"
                print(final_string)
                break

            ret_left, frame_left = self.cap_left.read()
            ret_right, frame_right = self.cap_right.read()

            if ret_left and ret_right:
                # Nhận diện với YOLO-pose
                results_left = self.model(frame_left)
                results_right = self.model(frame_right)

                # Xử lý và hiển thị keypoints cho camera bên trái
                annotated_frame_left = results_left[0].plot()
                self.best_frame_left = annotated_frame_left

                # Xử lý và hiển thị keypoints cho camera bên phải
                annotated_frame_right = results_right[0].plot()
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
                keypoints = r.keypoints.xy.cpu().numpy()[0]  # Lấy keypoints từ kết quả
                print("\nTọa độ các điểm:")
                for i, point in enumerate(keypoints):
                    point_name = keypoint_names.get(i, f"Điểm {i}")
                    print(f"{point_name}: (x: {point[0]:.2f}, y: {point[1]:.2f})")
    
    def process_keypoints(self, frame, side):
        """
        Xử lý và lưu keypoints vào định dạng yêu cầu
        """
        results = self.model(frame)
        
        for r in results:
            if r.keypoints is not None:
                keypoints = r.keypoints.xy.cpu().numpy()[0]  # shape: (6, 2) - chỉ có 6 keypoints
                
                # Điều chỉnh mapping cho phù hợp với 6 keypoints (0-5)
                huyet_points = {
                    "mauChiLyHoanhVan_left": (keypoints[0], keypoints[1]),  # Sử dụng keypoints 0,1
                    "lyNoiDinh_left": (keypoints[1], keypoints[2]),         # Sử dụng keypoints 1,2
                    "docAm_left": (keypoints[2], keypoints[3]),             # Sử dụng keypoints 2,3
                    "dungTuyen_left": (keypoints[3], keypoints[4]),         # Sử dụng keypoints 3,4
                    "tucTam_left": (keypoints[4], keypoints[5]),            # Sử dụng keypoints 4,5
                    "thatMien_left": (keypoints[0], keypoints[5])           # Sử dụng keypoints 0,5
                }
                
                # Tạo dữ liệu cho mỗi huyệt
                for huyet_name, (point1, point2) in huyet_points.items():
                    self.keypoints_data[huyet_name] = {
                        "xLeft": int(point1[0]),
                        "yLeft": int(point1[1]),
                        "xRight": int(point2[0]),
                        "yRight": int(point2[1])
                    }

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
                            "yLeft": y_coords[0],
                            "xRight": x_coords[1],
                            "yRight": y_coords[1]
                        }
                        print(f"Huyet {huyet_name} ({side}):")
                        print(f"  xLeft: {x_coords[0]}, yLeft: {y_coords[0]}")
                        print(f"  xRight: {x_coords[1]}, yRight: {y_coords[1]}")

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
        if frame is not None:
            # Xoay frame 90 độ ngay tại đây khi hiển thị
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

            # Chuyển đổi màu từ BGR sang RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

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
        self.is_detecting = False
        if self.cap_left.isOpened():
            self.cap_left.release()
        if self.cap_right.isOpened():
            self.cap_right.release()
        self.window.destroy()

    def start_pressing(self):
        self.status_var.set("Bắt đầu bấm huyệt...")
        print("*\n Start #\n")

    def stop_machine(self):
        self.status_var.set("Máy đã dừng.")

    def start_medicine(self):
        self.status_var.set("Bật dẫn dược.")

    def stop_medicine(self):
        self.status_var.set("Tắt dẫn dược.")

    def burn_medicine(self):
        self.status_var.set("Đang đốt dược liệu...")

    def stop_burn_medicine(self):
        self.status_var.set("Tắt đốt dược liệu.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MedicalControlApp(root, "BMD Machine Control V3.5")
    root.mainloop()