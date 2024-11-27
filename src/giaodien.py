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

        # self.model = YOLO('models/best-640-100eps.pt')
        self.model = YOLO('models/best-640-100eps.pt', task='pose')
        self.model.conf = 0.8 

        self.cap_left = cv2.VideoCapture('/home/thanthien/Coding/bmd-v3.5/video_test/1.mp4')
        self.cap_right = cv2.VideoCapture('/home/thanthien/Coding/bmd-v3.5/video_test/2.mp4')

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

        control_frame.columnconfigure(0, weight=1)

        treatment_label = ttk.Label(control_frame, text="Chọn bài bấm huyệt:", font=("Arial", 16))
        treatment_label.grid(row=0, column=0, sticky="W", pady=(0, 5))
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Large.TCombobox", 
                font=("Arial", 20),   # Increase font size
                padding=10)           # Add more padding

        # In the create_gui method, update the Combobox
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
            width=40,                 # Increase width
            font=("Arial", 16)        # Explicitly set font size
        )
        self.treatment_combo.grid(
            row=1, 
            column=0, 
            sticky="EW", 
            pady=(0, 10), 
            ipadx=10,                 # Increase internal x-padding
            ipady=10                  # Increase internal y-padding
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

    def rotate_frame(self, frame):
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
            if time.time() - self.detection_start_time >= 1:
                self.is_detecting = False
                self.status_var.set("Đã hoàn thành nhận diện")
                if hasattr(self, 'best_frame_left') and self.best_frame_left is not None:
                    print("\n--- Keypoints Camera Trái ---")
                    results_left = self.model(self.best_frame_left)
                    if len(results_left) > 0:
                        boxes_left = results_left[0].boxes
                        for i, box in enumerate(boxes_left):
                            if hasattr(box, 'keypoints') and box.keypoints is not None:
                                keypoints = box.keypoints.xy.cpu().numpy()[0]
                                print(f"Box {i} Keypoints:")
                                for j, kp in enumerate(keypoints):
                                    print(f"  Keypoint {j}: (x: {kp[0]:.2f}, y: {kp[1]:.2f})")
                
                # In ra tọa độ keypoints cho frame phải
                if hasattr(self, 'best_frame_right') and self.best_frame_right is not None:
                    print("\n--- Keypoints Camera Phải ---")
                    results_right = self.model(self.best_frame_right)
                    if len(results_right) > 0:
                        boxes_right = results_right[0].boxes
                        for i, box in enumerate(boxes_right):
                            if hasattr(box, 'keypoints') and box.keypoints is not None:
                                keypoints = box.keypoints.xy.cpu().numpy()[0]
                                print(f"Box {i} Keypoints:")
                                for j, kp in enumerate(keypoints):
                                    print(f"  Keypoint {j}: (x: {kp[0]:.2f}, y: {kp[1]:.2f})")
                break
            
            ret_left, frame_left = self.cap_left.read()
            ret_right, frame_right = self.cap_right.read()
            
            if ret_left and ret_right:
                results_left = self.model(frame_left)
                results_right = self.model(frame_right)
                
                # Xử lý camera bên trái
                if len(results_left) > 0:
                    boxes_left = results_left[0].boxes
                    high_conf_boxes_left = [box for box in boxes_left if box.conf.cpu().numpy()[0] > 0.8]
                    
                    if high_conf_boxes_left:
                        annotated_frame_left = frame_left.copy()
                        for box in high_conf_boxes_left:
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            conf = box.conf.cpu().numpy()[0]
                            
                            # Vẽ box
                            cv2.rectangle(annotated_frame_left, 
                                        (int(x1), int(y1)), 
                                        (int(x2), int(y2)), 
                                        (0, 255, 0),  # Màu xanh lá
                                        2)  # Độ dày đường viền
                            
                            # Vẽ các điểm (keypoints)
                            if hasattr(box, 'keypoints') and box.keypoints is not None:
                                keypoints = box.keypoints.xy.cpu().numpy()[0]
                                for kp in keypoints:
                                    # Vẽ điểm to và rõ
                                    cv2.circle(annotated_frame_left, 
                                            (int(kp[0]), int(kp[1])), 
                                            8,  # Bán kính lớn để dễ nhìn
                                            (0, 0, 255),  # Màu đỏ
                                            -1)  # Điền kín điểm
                            
                            # Thêm nhãn và độ tin cậy
                            label = f"{self.model.names[int(box.cls[0])]} {conf:.2f}"
                            cv2.putText(annotated_frame_left, 
                                        label, 
                                        (int(x1), int(y1 - 10)), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 
                                        0.5, 
                                        (0, 255, 0), 
                                        2)
                        
                        self.best_frame_left = annotated_frame_left
                        self.best_conf_left = max(box.conf.cpu().numpy()[0] for box in high_conf_boxes_left)
                
                # Tương tự cho camera bên phải
                if len(results_right) > 0:
                    boxes_right = results_right[0].boxes
                    high_conf_boxes_right = [box for box in boxes_right if box.conf.cpu().numpy()[0] > 0.8]
                    
                    if high_conf_boxes_right:
                        annotated_frame_right = frame_right.copy()
                        for box in high_conf_boxes_right:
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            conf = box.conf.cpu().numpy()[0]
                            
                            # Vẽ box
                            cv2.rectangle(annotated_frame_right, 
                                        (int(x1), int(y1)), 
                                        (int(x2), int(y2)), 
                                        (0, 255, 0),  # Màu xanh lá
                                        2)  # Độ dày đường viền
                            
                            # Vẽ các điểm (keypoints)
                            if hasattr(box, 'keypoints') and box.keypoints is not None:
                                keypoints = box.keypoints.xy.cpu().numpy()[0]
                                for kp in keypoints:
                                    # Vẽ điểm to và rõ
                                    cv2.circle(annotated_frame_right, 
                                            (int(kp[0]), int(kp[1])), 
                                            8,  # Bán kính lớn để dễ nhìn
                                            (0, 0, 255),  # Màu đỏ
                                            -1)  # Điền kín điểm
                            
                            # Thêm nhãn và độ tin cậy
                            label = f"{self.model.names[int(box.cls[0])]} {conf:.2f}"
                            cv2.putText(annotated_frame_right, 
                                        label, 
                                        (int(x1), int(y1 - 10)), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 
                                        0.5, 
                                        (0, 255, 0), 
                                        2)
                        
                        self.best_frame_right = annotated_frame_right
                        self.best_conf_right = max(box.conf.cpu().numpy()[0] for box in high_conf_boxes_right)

                frame_left = self.rotate_frame(frame_left)
                frame_right = self.rotate_frame(frame_right)

    
    def print_keypoints(self, results):
        """
        In ra thông tin keypoints từ kết quả YOLO
        """
        boxes = results.boxes
        for i, box in enumerate(boxes):
            if hasattr(box, 'keypoints') and box.keypoints is not None:
                keypoints = box.keypoints.xy.cpu().numpy()[0]
                print(f"Box {i} Keypoints:")
                for j, kp in enumerate(keypoints):
                    print(f"  Keypoint {j}: (x: {kp[0]:.2f}, y: {kp[1]:.2f})")

    def update_frames(self):
        if not self.is_detecting:
            if self.best_frame_left is not None and self.best_frame_right is not None:
                self.show_frame(self.best_frame_left, self.canvas_left)
                self.show_frame(self.best_frame_right, self.canvas_right)
            else:
                ret_left, frame_left = self.cap_left.read()
                ret_right, frame_right = self.cap_right.read()

                if ret_left and ret_right:
                    frame_left = self.rotate_frame(frame_left)
                    frame_right = self.rotate_frame(frame_right)

                    self.show_frame(frame_left, self.canvas_left)
                    self.show_frame(frame_right, self.canvas_right)

        self.window.after(10, self.update_frames)

    def show_frame(self, frame, canvas):
        # if frame is not None:
        #     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #     canvas.update_idletasks()
        #     canvas_width = canvas.winfo_width()
        #     canvas_height = canvas.winfo_height()
        #     if canvas_width > 1 and canvas_height > 1:
        #         frame = cv2.resize(frame, (canvas_width, canvas_height))
        #     photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
        #     canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        #     canvas.photo = photo
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