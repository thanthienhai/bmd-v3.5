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
        style.map("OnButton.TButton", foreground=[('pressed', 'white'), ('active', 'white')], background=[('pressed', 'green'), ('active', 'green')])
        style.map("OffButton.TButton", foreground=[('pressed', 'white'), ('active', 'white')], background=[('pressed', 'red'), ('active', 'red')])

        self.combo_font = ("Arial", 16)
        style.configure("Large.TCombobox", font=self.combo_font)

        self.model = YOLO('/home/ubuntu/Coding/swork/bmd-v3.5/models/best-1-1-24.pt')
        self.model.conf = 0.5

        self.cap_left = cv2.VideoCapture(4)
        self.cap_right = cv2.VideoCapture(2)
        self.cap_left.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap_left.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap_right.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap_right.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        ret_left, frame_left = self.cap_left.read()
        ret_right, frame_right = self.cap_right.read()
        if ret_left and ret_right:
            print(f"Camera trái: {frame_left.shape}")
            print(f"Camera phải: {frame_right.shape}")

        self.best_frame_left = None
        self.best_frame_right = None

        self.is_detecting = False
        self.uart = UARTManager(baudrate=115200)
        if not self.uart.is_connected:
            print("Cảnh báo: Không thể kết nối UART")

        self.original_width = 1280
        self.original_height = 720
        self.real_world_width = 250  # mm
        self.real_world_height = 120  # mm
        self.crop_width = 1160
        self.crop_height = 555

        self.scale_x = self.real_world_width / self.crop_width
        self.scale_y = self.real_world_height / self.crop_height

        self.crop_x_offset = (self.original_width - self.crop_width) / 2  # 60 pixels
        self.crop_y_offset = (self.original_height - self.crop_height) / 2  # 82.5 pixels

        self.keypoints_data = {}
        self.current_treatment = "1"
        self.state = "ready"  # States: ready, detecting, pressing

        self.create_gui()
        self.update_button_states()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def toggle_fullscreen(self, event=None):
        is_fullscreen = self.window.attributes("-fullscreen")
        self.window.attributes("-fullscreen", not is_fullscreen)

    def create_gui(self):
        # ... (Giữ nguyên phần tạo GUI)
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

        radio_frame = ttk.Frame(control_frame)
        radio_frame.grid(row=1, column=0, sticky="EW", pady=(0, 10))
        self.treatment_var = tk.StringVar(value="1")
        style = ttk.Style()
        style.configure("Custom.TRadiobutton", font=("Arial", 14), padding=5)
        treatments = [("Sốt, co giật", "1"), ("Stress", "2"), ("Thoát vị đĩa đệm", "3"), ("Bổ thận tráng dương", "4"), ("Nâng cao sức khỏe", "5")]
        for i, (text, value) in enumerate(treatments):
            radio = ttk.Radiobutton(radio_frame, text=text, value=value, variable=self.treatment_var, style="Custom.TRadiobutton", command=self.update_current_treatment)
            radio.grid(row=i, column=0, sticky="W", padx=20, pady=2)

        main_buttons_frame = ttk.LabelFrame(control_frame, text="Điều khiển chính", padding=2)
        main_buttons_frame.grid(row=2, column=0, sticky="EW", pady=5)
        self.detect_button = ttk.Button(main_buttons_frame, text="Nhận diện huyệt", command=self.start_detection)
        self.detect_button.grid(row=0, column=0, padx=5, pady=5, sticky="EW", ipadx=5)
        self.start_press_button = ttk.Button(main_buttons_frame, text="Bắt đầu bấm huyệt", command=self.start_pressing)
        self.start_press_button.grid(row=0, column=1, padx=5, pady=5, sticky="EW", ipadx=5)
        self.stop_button = ttk.Button(main_buttons_frame, text="Dừng máy", command=self.stop_machine)
        self.stop_button.grid(row=0, column=2, padx=5, pady=5, sticky="EW", ipadx=5)
        main_buttons_frame.columnconfigure(0, weight=1)
        main_buttons_frame.columnconfigure(1, weight=1)
        main_buttons_frame.columnconfigure(2, weight=1)

        medicine_frame = ttk.LabelFrame(control_frame, text="Điều khiển dẫn dược", padding=2)
        medicine_frame.grid(row=3, column=0, sticky="EW", pady=5)
        self.start_medicine_button = ttk.Button(medicine_frame, text="Bật dẫn dược", style="OnButton.TButton", command=self.start_medicine)
        self.start_medicine_button.grid(row=0, column=0, padx=5, pady=5, sticky="EW", ipadx=5)
        self.stop_medicine_button = ttk.Button(medicine_frame, text="Tắt dẫn dược", style="OffButton.TButton", command=self.stop_medicine)
        self.stop_medicine_button.grid(row=0, column=1, padx=5, pady=5, sticky="EW", ipadx=5)
        medicine_frame.columnconfigure(0, weight=1)
        medicine_frame.columnconfigure(1, weight=1)

        burning_frame = ttk.LabelFrame(control_frame, text="Điều khiển đốt dược liệu", padding=2)
        burning_frame.grid(row=4, column=0, sticky="EW", pady=5)
        self.burn_button = ttk.Button(burning_frame, text="Đốt dược liệu", style="OnButton.TButton", command=self.burn_medicine)
        self.burn_button.grid(row=0, column=0, padx=5, pady=5, sticky="EW", ipadx=5)
        self.stop_burn_button = ttk.Button(burning_frame, text="Tắt đốt dược liệu", style="OffButton.TButton", command=self.stop_burn_medicine)
        self.stop_burn_button.grid(row=0, column=1, padx=5, pady=5, sticky="EW", ipadx=5)
        burning_frame.columnconfigure(0, weight=1)
        burning_frame.columnconfigure(1, weight=1)

        exit_button = ttk.Button(control_frame, text="THOÁT", command=self.on_closing)
        exit_button.grid(row=5, column=0, sticky="EW", pady=15, ipadx=5)

        self.status_var = tk.StringVar()
        self.status_var.set("Sẵn sàng")
        status_bar = ttk.Label(self.window, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=2)
        status_bar.grid(row=1, column=0, sticky="EW")

        self.update_frames()

    def update_current_treatment(self):
        self.current_treatment = self.treatment_var.get()

    def update_button_states(self):
        self.detect_button['state'] = 'normal' if self.state == 'ready' else 'disabled'
        self.start_press_button['state'] = 'normal' if self.state == 'ready' and self.keypoints_data else 'disabled'
        self.stop_button['state'] = 'normal' if self.state == 'pressing' else 'disabled'

    def start_detection(self):
        if self.state == 'ready':
            self.state = 'detecting'
            self.update_button_states()
            self.status_var.set("Đang nhận diện huyệt...")
            self.keypoints_data = {}
            self.best_frame_left = None  # Reset best frames
            self.best_frame_right = None
            threading.Thread(target=self.perform_detection, daemon=True).start()

    def perform_detection(self):
        try:
            ret_left, full_frame_left = self.cap_left.read()
            ret_right, full_frame_right = self.cap_right.read()

            if not ret_left or not ret_right:
                self.status_var.set("Lỗi đọc camera.")
                self.state = 'ready'
                self.update_button_states()
                return

            frame_left_cropped = full_frame_left[self.crop_coords[1]:self.crop_coords[1] + self.crop_height,
                                                 self.crop_coords[0]:self.crop_coords[0] + self.crop_width].copy() # Thêm .copy()
            frame_right_cropped = full_frame_right[self.crop_coords[1]:self.crop_coords[1] + self.crop_height,
                                                  self.crop_coords[0]:self.crop_coords[0] + self.crop_width].copy() # Thêm .copy()

            results_left = self.model(frame_left_cropped)
            results_right = self.model(frame_right_cropped)

            annotated_frame_left = results_left[0].plot(kpt_radius=12)
            annotated_frame_right = results_right[0].plot(kpt_radius=12)

            self.best_frame_left = annotated_frame_left
            self.best_frame_right = annotated_frame_right

            self.process_keypoints(self.best_frame_left, "left") # Process on the annotated frame
            self.process_keypoints(self.best_frame_right, "right") # Process on the annotated frame

            self.keypoints_data["baiBamHuyet"] = int(self.current_treatment)

            self.status_var.set("Đã nhận diện huyệt thành công.")
            self.state = 'ready'
            self.update_button_states()

        except Exception as e:
            print(f"Lỗi trong quá trình nhận diện: {e}")
            self.status_var.set(f"Lỗi nhận diện: {e}")
            self.state = 'ready'
            self.update_button_states()

    def process_keypoints(self, frame, side):
        results = self.model(frame)
        frame_height, frame_width = frame.shape[:2]

        for r in results:
            if r.keypoints is not None and len(r.keypoints.xy) > 0:
                keypoints = r.keypoints.xy.cpu().numpy()[0]
                huyet_names = ["mauChiLyHoanhVan", "lyNoiDinh", "docAm", "dungTuyen", "tucTam", "thatMien"]
                for i, huyet_name in enumerate(huyet_names):
                    try:
                        yolo_coords = keypoints[i]
                        pixel_x, pixel_y = int(round(yolo_coords[0])), int(round(yolo_coords[1]))

                        # Kiểm tra xem điểm có nằm trong vùng crop không
                        if self.is_point_in_crop_area(pixel_x + self.crop_x_offset, pixel_y + self.crop_y_offset):
                            x_machine, y_machine = self.convert_pixel_to_machine((pixel_x, pixel_y))

                            if huyet_name not in self.keypoints_data:
                                self.keypoints_data[huyet_name] = {"xLeft": 0, "yLeft": 0, "xRight": 0, "yRight": 0}

                            if side == "left":
                                self.keypoints_data[huyet_name]["xLeft"] = x_machine
                                self.keypoints_data[huyet_name]["yLeft"] = y_machine
                            elif side == "right":
                                self.keypoints_data[huyet_name]["xRight"] = x_machine
                                self.keypoints_data[huyet_name]["yRight"] = y_machine

                            self.display_coordinates(frame, (pixel_x, pixel_y), (x_machine, y_machine), huyet_name, side)

                    except (IndexError, ValueError) as e:
                        print(f"Lỗi xử lý huyệt {huyet_name}: {str(e)}")
                        if huyet_name not in self.keypoints_data:
                            self.keypoints_data[huyet_name] = {"xLeft": 0, "yLeft": 0, "xRight": 0, "yRight": 0}
        return frame

    def display_coordinates(self, frame, pixel_coords, machine_coords, huyet_name, side):
        pixel_x, pixel_y = pixel_coords
        machine_x, machine_y = machine_coords
        cv2.circle(frame, (pixel_x, pixel_y), 5, (0, 255, 0), -1)
        text = f"{huyet_name}_{side}: Pixel({pixel_x},{pixel_y}) -> Machine({machine_x},{machine_y})"
        cv2.putText(frame, text, (pixel_x + 10, pixel_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    def start_pressing(self):
        if self.state == 'ready' and self.keypoints_data:
            self.state = 'pressing'
            self.update_button_states()
            self.status_var.set("Bắt đầu bấm huyệt...")
            json_string = json.dumps(self.keypoints_data, indent=2)
            final_string = f"*\n {json_string} #\n"
            print(final_string)
            if self.uart.is_connected:
                if self.uart.send_data(final_string):
                    self.status_var.set("Đã gửi dữ liệu bấm huyệt.")
                else:
                    self.status_var.set("Lỗi gửi dữ liệu bấm huyệt qua UART.")
            else:
                self.status_var.set("Không thể gửi lệnh: UART chưa được kết nối")

    def stop_machine(self):
        if self.state == 'pressing':
            self.state = 'ready'
            self.update_button_states()
            self.status_var.set("Dừng máy.")
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

    def convert_pixel_to_machine(self, pixel_coords, is_cropped_image=False):
        """
        Chuyển đổi tọa độ pixel sang tọa độ máy (mm)
        pixel_coords: (x, y) tọa độ pixel
        is_cropped_image: True nếu tọa độ đã được crop, False nếu là tọa độ gốc
        """
        pixel_x, pixel_y = pixel_coords

        if not is_cropped_image:
            # Điều chỉnh offset cho vùng crop
            adjusted_x = pixel_x - self.crop_x_offset
            adjusted_y = pixel_y - self.crop_y_offset
        else:
            adjusted_x = pixel_x
            adjusted_y = pixel_y

        # Kiểm tra tọa độ có nằm trong vùng crop
        if (adjusted_x < 0 or adjusted_x >= self.crop_width or 
            adjusted_y < 0 or adjusted_y >= self.crop_height):
            return None  # Điểm nằm ngoài vùng crop

        # Chuyển đổi sang tọa độ máy
        machine_x = int(round(adjusted_x * self.scale_x))
        machine_y = int(round(adjusted_y * self.scale_y))

        return machine_x, machine_y

    def is_point_in_crop_area(self, x, y):
        """Kiểm tra xem điểm có nằm trong vùng crop không"""
        adjusted_x = x - self.crop_x_offset
        adjusted_y = y - self.crop_y_offset
        
        return (0 <= adjusted_x < self.crop_width and 
                0 <= adjusted_y < self.crop_height)

    def update_frames(self):
        if self.state == 'ready' and self.best_frame_left is not None and self.best_frame_right is not None:
            # Hiển thị frame tốt nhất sau khi nhận diện
            best_frame_left = self.draw_points_on_grid(self.best_frame_left.copy(), "left")
            best_frame_right = self.draw_points_on_grid(self.best_frame_right.copy(), "right")
            self.show_frame(self.best_frame_left, self.canvas_left)
            self.show_frame(self.best_frame_right, self.canvas_right)
        elif self.state != 'detecting':
            # Hiển thị luồng camera trực tiếp khi không nhận diện
            ret_left, full_frame_left = self.cap_left.read()
            ret_right, full_frame_right = self.cap_right.read()
            if ret_left and ret_right:
                frame_left_cropped = full_frame_left[self.crop_coords[1]:self.crop_coords[1] + self.crop_height,
                                                     self.crop_coords[0]:self.crop_coords[0] + self.crop_width]
                frame_right_cropped = full_frame_right[self.crop_coords[1]:self.crop_coords[1] + self.crop_height,
                                                      self.crop_coords[0]:self.crop_coords[0] + self.crop_width]
                self.show_frame(frame_left_cropped, self.canvas_left)
                self.show_frame(frame_right_cropped, self.canvas_right)
        elif self.state == 'detecting':
            # Trong quá trình nhận diện, có thể hiển thị một frame chờ hoặc giữ nguyên frame cuối cùng
            pass # Giữ nguyên frame cuối cùng

        self.window.after(10, self.update_frames)

    def show_frame(self, frame, canvas):
        if frame is not None:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, 1)
            canvas.update_idletasks()
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            if canvas_width > 1 and canvas_height > 1:
                frame_height, frame_width = frame.shape[:2]
                scale = min(canvas_width / frame_width, canvas_height / frame_height)
                new_width = int(frame_width * scale)
                new_height = int(frame_height * scale)
                frame_resized = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
                photo = ImageTk.PhotoImage(image=Image.fromarray(frame_resized))
                canvas.delete("all")
                canvas.create_image(canvas_width / 2, canvas_height / 2, image=photo, anchor=tk.CENTER)
                canvas.photo = photo

    def on_closing(self):
        self.is_detecting = False
        if hasattr(self, 'uart'):
            self.uart.close()
        if self.cap_left.isOpened():
            self.cap_left.release()
        if self.cap_right.isOpened():
            self.cap_right.release()
        self.window.destroy()
    
    def draw_points_on_grid(self, frame, side):
        """
        Vẽ các điểm đại diện cho keypoints lên grid dựa trên tọa độ máy.
        """
        if side == "left":
            x_offset = self.crop_x_offset
            y_offset = self.crop_y_offset
        else:  # side == "right"
            x_offset = self.crop_x_offset
            y_offset = self.crop_y_offset

        for huyet_name, coords in self.keypoints_data.items():
            if side == "left" and coords["xLeft"] != 0 and coords["yLeft"] != 0:
                # Chuyển đổi tọa độ máy sang pixel trên frame (đã crop)
                pixel_x = int(coords["xLeft"] / self.scale_x) + int(x_offset)
                pixel_y = int(coords["yLeft"] / self.scale_y) + int(y_offset)

                # Vẽ điểm lên frame
                cv2.circle(frame, (pixel_x, pixel_y), 5, (255, 0, 0), -1)  # Màu đỏ

            elif side == "right" and coords["xRight"] != 0 and coords["yRight"] != 0:
                # Chuyển đổi tọa độ máy sang pixel trên frame (đã crop)
                pixel_x = int(coords["xRight"] / self.scale_x) + int(x_offset)
                pixel_y = int(coords["yRight"] / self.scale_y) + int(y_offset)

                # Vẽ điểm lên frame
                cv2.circle(frame, (pixel_x, pixel_y), 5, (255, 0, 0), -1)  # Màu đỏ
        return frame

if __name__ == "__main__":
    root = tk.Tk()
    app = MedicalControlApp(root, "BMD Machine Control V3.5")
    root.mainloop()