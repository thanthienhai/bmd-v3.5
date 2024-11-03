import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import threading

class MassageControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Điều khiển massage bấm huyệt")
        
        # Create main interface frames
        self.left_frame = tk.Frame(root, width=400, height=300, bg="white")  # For camera feed
        self.left_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
        
        self.control_frame = tk.Frame(root, bg="lightgray")  # Control panel
        self.control_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Camera display frames
        self.camera_left_label = tk.Label(self.left_frame, text="Camera Left")
        self.camera_left_label.grid(row=0, column=0)
        
        self.camera_right_label = tk.Label(self.left_frame, text="Camera Right")
        self.camera_right_label.grid(row=1, column=0)

        # Control buttons
        self.start_button = tk.Button(self.control_frame, text="Bắt đầu bấm huyệt", command=self.start_cameras)
        self.start_button.grid(row=0, column=0, padx=10, pady=5)
        
        self.stop_button = tk.Button(self.control_frame, text="Dừng máy", command=self.stop_cameras)
        self.stop_button.grid(row=1, column=0, padx=10, pady=5)
        
        # Dropdown menu for selecting massage routine
        self.routine_label = tk.Label(self.control_frame, text="Chọn bài bấm huyệt:")
        self.routine_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.routine_var = tk.StringVar()
        self.routine_menu = ttk.Combobox(self.control_frame, textvariable=self.routine_var)
        self.routine_menu['values'] = ["Bài 1", "Bài 2", "Bài 3"]
        self.routine_menu.grid(row=3, column=0, padx=10, pady=5)
        
        # Additional control buttons
        self.buttons_frame = tk.Frame(self.control_frame)
        self.buttons_frame.grid(row=4, column=0, pady=10)

        tk.Button(self.buttons_frame, text="Bật dẫn được").grid(row=0, column=0, padx=5, pady=5)
        tk.Button(self.buttons_frame, text="Tắt dẫn được").grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.buttons_frame, text="Đốt dược liệu").grid(row=1, column=0, padx=5, pady=5)
        tk.Button(self.buttons_frame, text="Tắt đốt dược liệu").grid(row=1, column=1, padx=5, pady=5)

        # Camera and threading setup
        self.cap_left = None
        self.cap_right = None
        self.running = False

    def start_cameras(self):
        if not self.running:
            self.running = True
            # Open cameras
            self.cap_left = cv2.VideoCapture(0)
            self.cap_right = cv2.VideoCapture(1)
            # Start camera update threads
            threading.Thread(target=self.update_camera_left).start()
            threading.Thread(target=self.update_camera_right).start()

    def stop_cameras(self):
        self.running = False
        if self.cap_left:
            self.cap_left.release()
        if self.cap_right:
            self.cap_right.release()
        self.camera_left_label.config(image='')
        self.camera_right_label.config(image='')

    def update_camera_left(self):
        while self.running and self.cap_left.isOpened():
            ret, frame = self.cap_left.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.camera_left_label.imgtk = imgtk
                self.camera_left_label.config(image=imgtk)
            else:
                break

    def update_camera_right(self):
        while self.running and self.cap_right.isOpened():
            ret, frame = self.cap_right.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.camera_right_label.imgtk = imgtk
                self.camera_right_label.config(image=imgtk)
            else:
                break

    def on_closing(self):
        self.stop_cameras()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MassageControlApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
