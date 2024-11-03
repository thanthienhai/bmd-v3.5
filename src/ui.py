import sys
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
from ultralytics import YOLO

# Thread riêng cho camera capture
class CameraThread(QThread):
    frame_ready = pyqtSignal(np.ndarray)

    def __init__(self, camera_id=0):
        super().__init__()
        self.callback = callback
        self.running = False
        self.camera_id = 0

    def run(self):
        # cap = cv2.VideoCapture(self.camera_id)
        video_path = 'video_test/video.mp4'
        cap = cv2.VideoCapture(video_path)
        self.running = True
        
        while self.running:
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.callback(frame)
            self.event = threading.Event()
            self.event.wait(0.03)
            
        cap.release()

    def stop(self):
        self.running = False
        self.join()

class CustomButton(ttk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

    def on_enter(self, e):
        self.state(['pressed'])

    def on_leave(self, e):
        self.state(['!pressed'])

class BMDMachineControl:
    def __init__(self, root):
        self.root = root
        self.root.title("BMD Machine Control V3.5")
        self.root.geometry("1280x960")
        
        # Set theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure custom styles
        self.configure_styles()
        
        try:
            self.detector = FootAcupointDetector("models/yolo_pose_model.pt")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.detector = None
        
        # States
        self.medicine_on = False
        self.herb_on = False
        self.is_processing = False
        
        # Create main container
        self.main_container = ttk.Frame(root, padding="10")
        self.main_container.pack(fill='both', expand=True)
        
        # Create notebook with custom style
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create tabs with custom styling
        self.massage_tab = ttk.Frame(self.notebook, padding="10")
        self.routine_tab = ttk.Frame(self.notebook, padding="10")
        self.settings_tab = ttk.Frame(self.notebook, padding="10")
        
        self.notebook.add(self.massage_tab, text=" Massage bàn chân ")
        self.notebook.add(self.routine_tab, text=" Tạo bài bấm huyệt ")
        self.notebook.add(self.settings_tab, text=" Cài đặt ")
        
        self.setup_massage_tab()
        self.setup_routine_tab()
        self.setup_settings_tab()
        
        self.camera_thread = CameraThread(self.process_frame)
        
        # Add status bar
        self.setup_status_bar()

    def createFootMassageTab(self):
        tab = QWidget()

        # Màn hình bên trái và phải
        self.left_display = QLabel()
        self.left_display.setAlignment(Qt.AlignCenter)
        self.left_display.setStyleSheet("background-color: #f0f0f0;")
        self.left_display.setMinimumSize(320, 240)
        
        self.right_display = QLabel()
        self.right_display.setAlignment(Qt.AlignCenter)
        self.right_display.setStyleSheet("background-color: #a0a0a0;")
        self.right_display.setMinimumSize(320, 240)

        # Các control khác
        routine_selection = QComboBox()
        routine_selection.addItems(["Sốt, co giật", "Stress", "Thoát vị đĩa đệm", "Bổ thận tráng dương", "Nâng cao sức khỏe"])

        self.start_button = QPushButton("Bắt đầu bấm huyệt")
        self.start_button.setStyleSheet("background-color: #00ff00; color: black; font-weight: bold;")
        self.start_button.setFixedHeight(100)
        self.start_button.clicked.connect(self.start_massage)
        
        self.stop_button = QPushButton("Dừng máy")
        self.stop_button.setStyleSheet("background-color: #ff0000; color: black; font-weight: bold;")
        self.stop_button.clicked.connect(self.stop_massage)

        self.btn_on_medicine = QPushButton("Bật dẫn dược")
        self.btn_off_medicine = QPushButton("Tắt dẫn dược")
        self.btn_on_herb = QPushButton("Đốt dược liệu")
        self.btn_off_herb = QPushButton("Tắt đốt dược liệu")

        self.btn_on_medicine.clicked.connect(self.toggle_medicine)
        self.btn_off_medicine.clicked.connect(self.toggle_medicine)
        self.btn_on_herb.clicked.connect(self.toggle_herb)
        self.btn_off_herb.clicked.connect(self.toggle_herb)

        self.status_display = QLabel("Đang chờ...")
        self.status_display.setAlignment(Qt.AlignCenter)
        
        self.start_button = CustomButton(control_buttons_frame, 
                                       text="Bắt đầu bấm huyệt",
                                       style='Success.TButton',
                                       command=self.start_massage)
        self.start_button.pack(fill='x', pady=2)
        
        self.stop_button = CustomButton(control_buttons_frame, 
                                      text="Dừng máy",
                                      style='Danger.TButton',
                                      command=self.stop_massage)
        self.stop_button.pack(fill='x', pady=2)

    def setup_routine_tab(self):
        # Title
        title = ttk.Label(self.routine_tab, 
                         text="Tạo và quản lý bài bấm huyệt",
                         style='Title.TLabel')
        title.pack(fill='x', pady=(0, 20))
        
        # Placeholder content with better styling
        content_frame = ttk.Frame(self.routine_tab, padding="20")
        content_frame.pack(fill='both', expand=True)
        
        placeholder = ttk.Label(content_frame,
                              text="Tính năng đang được phát triển...",
                              font=('Helvetica', 12))
        placeholder.pack(expand=True)

    def setup_settings_tab(self):
        # Title
        title = ttk.Label(self.settings_tab, 
                         text="Cài đặt hệ thống",
                         style='Title.TLabel')
        title.pack(fill='x', pady=(0, 20))
        
        # Placeholder content with better styling
        content_frame = ttk.Frame(self.settings_tab, padding="20")
        content_frame.pack(fill='both', expand=True)
        
        placeholder = ttk.Label(content_frame,
                              text="Tính năng đang được phát triển...",
                              font=('Helvetica', 12))
        placeholder.pack(expand=True)

    def setup_status_bar(self):
        # Create status bar
        status_frame = ttk.Frame(self.root, relief='sunken', padding="5")
        status_frame.pack(side='bottom', fill='x')
        
        self.status_display = ttk.Label(status_frame, 
                                      text="Sẵn sàng",
                                      style='Status.TLabel')
        self.status_display.pack(side='left')
        
        # Add version info
        version_label = ttk.Label(status_frame,
                                text="v3.5",
                                style='Status.TLabel')
        version_label.pack(side='right')

    def process_frame(self, frame):
        # Process frame logic remains the same
        if self.is_processing and self.detector is not None:
            try:
                keypoints = self.detector.detect_acupoints(frame)
                processed_frame = self.detector.visualize_keypoints(frame.copy(), 
                                                                 keypoints)
                image = Image.fromarray(processed_frame)
                photo = ImageTk.PhotoImage(image)
                self.left_display.configure(image=photo)
                self.left_display.image = photo
            except Exception as e:
                print(f"Error processing frame: {e}")
        else:
            # Hiển thị frame gốc nếu không trong trạng thái xử lý
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.left_display.setPixmap(QPixmap.fromImage(q_img).scaled(
                self.left_display.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def start_massage(self):
        self.is_processing = True
        self.camera_thread.start()
        self.status_display.configure(text="Đang thực hiện bấm huyệt...")
        self.start_button.state(['disabled'])
        self.stop_button.state(['!disabled'])

    def stop_massage(self):
        self.is_processing = False
        self.camera_thread.stop()
        self.status_display.configure(text="Đã dừng")
        self.start_button.state(['!disabled'])
        self.stop_button.state(['disabled'])

    def toggle_medicine(self):
        self.medicine_on = not self.medicine_on
        if self.medicine_on:
            self.btn_on_medicine.state(['disabled'])
            self.btn_off_medicine.state(['!disabled'])
            self.status_display.configure(text="Đã bật dẫn dược")
        else:
            self.btn_on_medicine.state(['!disabled'])
            self.btn_off_medicine.state(['disabled'])
            self.status_display.configure(text="Đã tắt dẫn dược")

    def toggle_herb(self):
        self.herb_on = not self.herb_on
        if self.herb_on:
            self.btn_on_herb.state(['disabled'])
            self.btn_off_herb.state(['!disabled'])
            self.status_display.configure(text="Đã bật đốt dược liệu")
        else:
            self.btn_on_herb.state(['!disabled'])
            self.btn_off_herb.state(['disabled'])
            self.status_display.configure(text="Đã tắt đốt dược liệu")

def main():
    try:
        # Use ThemedTk instead of regular Tk for better looking widgets
        root = ThemedTk(theme="clam")
        root.configure(bg='#f0f0f0')
        
        # Set window icon (if you have one)
        
        # Make window responsive
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # Create splash screen
        splash = create_splash_screen(root)
        
        # Initialize application
        app = BMDMachineControl(root)
        
        # Destroy splash screen after 2 seconds
        root.after(2000, splash.destroy)
        
        # Center window on screen
        center_window(root)
        
        # Start main loop
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    main()