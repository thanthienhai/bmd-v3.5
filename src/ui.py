import sys
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
from ultralytics import YOLO
from ttkthemes import ThemedTk
from processing import FootAcupointDetector
import time

class CameraThread(threading.Thread):
    def __init__(self, callback):
        super().__init__(daemon=True)
        self.callback = callback
        self.running = False
        self.camera_id = 0
        self.event = threading.Event()  # Initialize the event here

    def run(self):
        try:
            video_path = 'video_test/1.mp4'
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print("Error: Unable to open video source.")
                return

            self.running = True

            while self.running:
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.callback(frame)
                else:
                    print("End of video stream or cannot read the frame.")
                    break  # Exit the loop if frame not read

                self.event.wait(0.03)  # Control frame rate

            cap.release()
        except Exception as e:
            print(f"Exception in CameraThread: {e}")
            cap.release()

    def stop(self):
        if self.is_alive():
            print("Stopping CameraThread...")
            self.running = False
            self.event.set()  # Unblock the wait if it's waiting
            self.join(timeout=2)  # Đặt timeout để tránh treo
            if self.is_alive():
                print("Warning: CameraThread did not terminate in time.")
            else:
                print("CameraThread successfully stopped.")

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
        # Geometry settings are managed in the main function
        # self.root.geometry("1024x600")  # Removed from here

        # Set theme and configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()

        # Initialize detector
        try:
            self.detector = FootAcupointDetector("models/best_9_11.pt")
            print("Đã khởi tạo detector thành công")
        except Exception as e:
            print(f"Lỗi khi khởi tạo detector: {e}")
            self.detector = None

        # States
        self.medicine_on = False
        self.herb_on = False
        self.is_processing = False

        # Create main container and notebook
        self.main_container = ttk.Frame(root, padding="10")
        self.main_container.pack(fill='both', expand=True)
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Create tabs
        self.massage_tab = ttk.Frame(self.notebook, padding="5")
        self.routine_tab = ttk.Frame(self.notebook, padding="5")
        self.settings_tab = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(self.massage_tab, text=" Massage bàn chân ")
        self.notebook.add(self.routine_tab, text=" Tạo bài bấm huyệt ")
        self.notebook.add(self.settings_tab, text=" Cài đặt ")

        # Setup tabs
        self.setup_massage_tab()
        self.setup_routine_tab()
        self.setup_settings_tab()

        # Initialize camera thread as None
        self.camera_thread = None

        # Setup status bar
        self.setup_status_bar()

        # Bind the window close event to the handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Thêm các biến mới để theo dõi quá trình nhận diện
        self.detection_start_time = None
        self.best_frame = None
        self.best_confidence = 0
        self.is_detecting = False

    def configure_styles(self):
        # Configure colors
        primary_color = "#2196F3"  # Material Blue
        secondary_color = "#FFC107"  # Material Amber
        success_color = "#4CAF50"  # Material Green
        danger_color = "#F44336"  # Material Red

        # Calculate dynamic sizes based on window width
        def update_sizes(event=None):
            if hasattr(self, 'root'):
                window_width = self.root.winfo_width()
                window_height = self.root.winfo_height()

                # Adjust base size according to window width
                base_size = max(12, min(18, window_width // 60))  # Responsive font size tăng lên
                button_padding_x = max(10, min(20, window_width // 100))  # Horizontal padding
                button_padding_y = max(10, min(30, window_width // 60))  # Vertical padding tăng lên

                # Update button styles with larger font and padding
                self.style.configure('Primary.TButton',
                                padding=[button_padding_x, button_padding_y],
                                font=('Helvetica', base_size, 'bold'))

                self.style.configure('Success.TButton',
                                padding=[button_padding_x, button_padding_y],
                                font=('Helvetica', base_size, 'bold'))

                self.style.configure('Danger.TButton',
                                padding=[button_padding_x, button_padding_y],
                                font=('Helvetica', base_size, 'bold'))

                # Update label styles
                self.style.configure('Title.TLabel',
                                font=('Helvetica', base_size + 6, 'bold'),
                                padding=[0, button_padding_y])

                self.style.configure('Status.TLabel',
                                font=('Helvetica', base_size - 2),
                                padding=[button_padding_x//2, button_padding_y//2])

        # Initial style configuration
        self.style.configure('TNotebook.Tab', padding=[12, 8])

        # Button style maps
        self.style.map('Primary.TButton',
                    background=[('pressed', primary_color), ('active', primary_color)],
                    foreground=[('pressed', 'white'), ('active', 'white')])

        self.style.map('Success.TButton',
                    background=[('pressed', success_color), ('active', success_color)],
                    foreground=[('pressed', 'white'), ('active', 'white')])

        self.style.map('Danger.TButton',
                    background=[('pressed', danger_color), ('active', danger_color)],
                    foreground=[('pressed', 'white'), ('active', 'white')])

        # Bind the update_sizes function to window resize
        self.root.bind('<Configure>', update_sizes)
        # Initial call to set sizes
        update_sizes()

    def setup_massage_tab(self):
        # Title
        title = ttk.Label(self.massage_tab, 
                        text="Điều khiển massage bấm huyệt",
                        style='Title.TLabel')
        title.pack(fill='x', pady=(0, 20))

        # Create main content frame with two columns
        content_frame = ttk.Frame(self.massage_tab)
        content_frame.pack(fill='both', expand=True)

        # Left column - Display frame (takes up available space)
        display_frame = ttk.LabelFrame(content_frame, text="Hiển thị camera", padding="5")
        display_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))

        # Create a frame to hold the two camera displays side by side
        camera_frame = ttk.Frame(display_frame)
        camera_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Configure grid weights for camera frame
        camera_frame.grid_columnconfigure(0, weight=1)
        camera_frame.grid_columnconfigure(1, weight=1)
        camera_frame.grid_rowconfigure(0, weight=1)

        # Left camera display
        self.left_display = ttk.Label(camera_frame, relief='solid', borderwidth=1)
        self.left_display.grid(row=0, column=0, sticky='nsew', padx=(0, 2))

        # Right camera display
        self.right_display = ttk.Label(camera_frame, relief='solid', borderwidth=1)
        self.right_display.grid(row=0, column=1, sticky='nsew', padx=(2, 0))

        # Right column - Controls (30% of width)
        control_frame = ttk.LabelFrame(content_frame, text="Điều khiển", padding="5")
        control_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))

        # Make control frame elements expand horizontally
        control_frame.grid_columnconfigure(0, weight=1)

        # ====================== Tạo Frame Cho Các Nút Điều Khiển ======================
        # Sử dụng grid để sắp xếp các nút theo hàng ngang

        # Tạo một khung để chứa các nút điều khiển chính (Bắt đầu và Dừng)
        control_buttons_frame = ttk.Frame(control_frame)
        control_buttons_frame.pack(fill='x', pady=(0, 20))
        control_buttons_frame.grid_columnconfigure(0, weight=1)
        control_buttons_frame.grid_columnconfigure(1, weight=1)  # Thêm cấu hình cột

        # Nút Bắt đầu bấm huyệt
        self.start_button = CustomButton(control_buttons_frame, 
                                        text="Bắt đầu bấm huyệt",
                                        style='Success.TButton',
                                        command=self.start_massage,
                                        width=20)  # Đặt chiều rộng
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky='ew')  # Đặt ở cột 0

        # Nút Dừng máy
        self.stop_button = CustomButton(control_buttons_frame, 
                                        text="Dừng máy",
                                        style='Danger.TButton',
                                        command=self.stop_massage,
                                        width=20)  # Đặt chiều rộng
        self.stop_button.grid(row=0, column=1, padx=5, pady=5, sticky='ew')  # Đặt ở cột 1
        self.stop_button.state(['disabled'])  # Initially disabled

        # Thêm nút Nhận diện huyệt vào control_buttons_frame
        control_buttons_frame.grid_columnconfigure(2, weight=1)  # Thêm cột thứ 3
        
        self.detect_button = CustomButton(control_buttons_frame, 
                                        text="Nhận diện huyệt",
                                        style='Primary.TButton',
                                        command=self.start_detection,
                                        width=20)
        self.detect_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

        ttk.Label(control_frame, text="Chọn bài bấm huyệt:",
                font=('Helvetica', 10, 'bold')).pack(fill='x', pady=(0, 5))

        routines = ["Sốt, co giật", "Stress", "Thoát vị đĩa đệm", 
                    "Bổ thận tráng dương", "Nâng cao sức khỏe"]
        self.routine_var = tk.StringVar()

        # Tạo một Frame mới để chứa Combobox và nút tùy chỉnh
        combo_frame = ttk.Frame(control_frame)
        combo_frame.pack(fill='x', pady=(0, 20))  # Đảm bảo Frame này chiếm đủ chiều ngang

        # Thêm Combobox vào Frame và căn lề trái
        routine_combo = ttk.Combobox(combo_frame, 
                                    textvariable=self.routine_var,
                                    values=routines,
                                    width=35,  
                                    font=('Helvetica', 18))
        routine_combo.pack(side='left', fill='x', expand=True)  # Sử dụng pack với side='left'

        # Thêm nút tùy chỉnh vào Frame và căn lề phải
        dropdown_button = ttk.Button(combo_frame, 
                                    text="▼", 
                                    command=lambda: routine_combo.event_generate('<Button-1>'))
        dropdown_button.pack(side='left', padx=(5, 0))  # Căn bên cạnh combobox với khoảng cách nhỏ

        # ====================== Điều Khiển Dẫn Dược ======================
        # Medicine control group
        medicine_frame = ttk.LabelFrame(control_frame, text="Điều khiển dẫn dược", padding="5")
        medicine_frame.pack(fill='x', pady=(0, 10))
        medicine_frame.grid_columnconfigure(0, weight=1)
        medicine_frame.grid_columnconfigure(1, weight=1)  # Thêm cấu hình cột

        # Sử dụng grid để đặt các nút cùng hàng
        self.btn_on_medicine = CustomButton(medicine_frame, 
                                            text="Bật dẫn dược",
                                            style='Success.TButton',
                                            command=self.toggle_medicine,
                                            width=15)  # Đặt chiều rộng
        self.btn_on_medicine.grid(row=0, column=0, padx=5, pady=5, sticky='ew')  # Đặt ở cột 0

        self.btn_off_medicine = CustomButton(medicine_frame, 
                                            text="Tắt dẫn dược",
                                            style='Danger.TButton',
                                            command=self.toggle_medicine,
                                            width=15)  # Đặt chiều rộng
        self.btn_off_medicine.grid(row=0, column=1, padx=5, pady=5, sticky='ew')  # Đặt ở cột 1
        self.btn_off_medicine.state(['disabled'])  # Initially disabled

        # ====================== Điều Khiển Dược Liệu ======================
        # Herb control group with grid layout
        herb_frame = ttk.LabelFrame(control_frame, text="Điều khiển dược liệu", padding="5")
        herb_frame.pack(fill='x', pady=(0, 10))
        herb_frame.grid_columnconfigure(0, weight=1)
        herb_frame.grid_columnconfigure(1, weight=1)  # Thêm cấu hình cột

        # Sử dụng grid để đặt các nút cùng hàng
        self.btn_on_herb = CustomButton(herb_frame, 
                                        text="Đốt dược liệu",
                                        style='Success.TButton',
                                        command=self.toggle_herb,
                                        width=15)  # Đặt chiều rộng
        self.btn_on_herb.grid(row=0, column=0, padx=5, pady=5, sticky='ew')  # Đặt ở cột 0

        self.btn_off_herb = CustomButton(herb_frame, 
                                        text="Tắt đốt dược liệu",
                                        style='Danger.TButton',
                                        command=self.toggle_herb,
                                        width=15)  # Đặt chiều rộng
        self.btn_off_herb.grid(row=0, column=1, padx=5, pady=5, sticky='ew')  # Đặt ở cột 1
        self.btn_off_herb.state(['disabled'])  # Initially disabled
        
        # ====================== Thêm Nút 'THOÁT' ======================
        # Tạo một khung mới để chứa nút 'THOÁT'
        exit_frame = ttk.Frame(control_frame)
        exit_frame.pack(fill='x', pady=(10, 0))  # Thêm khoảng cách trên nút

        # Thêm nút 'THOÁT' vào exit_frame
        exit_button = CustomButton(exit_frame, 
                                text="THOÁT", 
                                style='Danger.TButton', 
                                command=self.on_closing)
        exit_button.pack(pady=5)  # Đặt nút với khoảng cách trên và dưới


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
        
        # Thêm nút 'THOÁT' dưới placeholder
        exit_button = CustomButton(content_frame, 
                                text="THOÁT", 
                                style='Danger.TButton', 
                                command=self.on_closing)
        exit_button.pack(pady=20)

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
        # Rotate frame 90 degrees
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        # Get display dimensions
        display_width = self.left_display.winfo_width()
        display_height = self.left_display.winfo_height()

        if display_width > 1 and display_height > 1:
            # Calculate aspect ratio
            frame_height, frame_width = frame.shape[:2]
            aspect_ratio = frame_width / frame_height

            # Determine new size maintaining aspect ratio
            if (display_width / display_height) > aspect_ratio:
                new_height = display_height
                new_width = int(display_height * aspect_ratio)
            else:
                new_width = display_width
                new_height = int(display_width / aspect_ratio)

            # Resize frame
            frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

        if self.is_detecting and self.detector is not None:
            try:
                # Kiểm tra thời gian đã trôi qua
                elapsed_time = time.time() - self.detection_start_time
                
                if elapsed_time <= 5.0:  # Trong khoảng 5 giây
                    # Detect keypoints
                    keypoints, confidences = self.detector.detect_acupoints(frame)
                    
                    # Tính toán độ tin cậy trung bình của frame hiện tại
                    if confidences and len(confidences) > 0:
                        current_confidence = sum(confidences) / len(confidences)
                        
                        # Cập nhật frame tốt nhất nếu có độ tin cậy cao hơn
                        if current_confidence > self.best_confidence:
                            self.best_confidence = current_confidence
                            self.best_frame = frame.copy()
                            
                    # Hiển thị frame hiện tại với keypoints
                    processed_frame = self.detector.visualize_keypoints(frame.copy(), keypoints)
                    self.root.after(0, self.update_gui, processed_frame, frame)
                    
                else:  # Hết 5 giây
                    self.is_detecting = False
                    self.detect_button.state(['!disabled'])
                    
                    if self.best_frame is not None:
                        # Hiển thị frame tốt nhất
                        keypoints, _ = self.detector.detect_acupoints(self.best_frame)
                        best_processed = self.detector.visualize_keypoints(self.best_frame.copy(), keypoints)
                        self.root.after(0, self.update_gui, best_processed, self.best_frame)
                        self.status_display.configure(
                            text=f"Nhận diện hoàn tất - Độ tin cậy: {self.best_confidence:.2f}")
                    else:
                        self.status_display.configure(text="Không tìm thấy huyệt đạo phù hợp")

            except Exception as e:
                print(f"Lỗi xử lý frame: {e}")
                self.root.after(0, self.update_gui, frame, frame)
        else:
            # Hiển thị frame gốc nếu không trong quá trình nhận diện
            self.root.after(0, self.update_gui, frame, frame)

    def update_gui(self, processed_frame, original_frame):
        # Update the left display with processed frame
        image = Image.fromarray(processed_frame)
        photo = ImageTk.PhotoImage(image)
        self.left_display.configure(image=photo)
        self.left_display.image = photo  # Prevent garbage collection

        # Update the right display with original frame
        original_image = Image.fromarray(original_frame)
        original_photo = ImageTk.PhotoImage(original_image)
        self.right_display.configure(image=original_photo)
        self.right_display.image = original_photo  # Prevent garbage collection

    def start_massage(self):
        if not self.is_processing:
            self.is_processing = True
            # Initialize a new CameraThread instance
            self.camera_thread = CameraThread(self.process_frame)
            self.camera_thread.start()
            self.status_display.configure(text="Đang thực hiện bấm huyệt...")
            self.start_button.state(['disabled'])
            self.stop_button.state(['!disabled'])

    def stop_massage(self):
        if self.is_processing and self.camera_thread is not None:
            self.is_processing = False
            self.camera_thread.stop()
            self.camera_thread = None  # Reset the thread instance
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

    def on_closing(self):
        """
        Handler for the window close event.
        Ensures that the camera thread is stopped before closing the application.
        """
        if self.is_processing:
            if messagebox.askokcancel("Quit", "Processing is ongoing. Do you want to stop and exit?"):
                self.stop_massage()
            else:
                return  # Do not close the window
        self.root.destroy()

    def start_detection(self):
        """Bắt đầu quá trình nhận diện 5 giây"""
        if not self.is_detecting:
            self.is_detecting = True
            self.detection_start_time = time.time()
            self.best_frame = None
            self.best_confidence = 0
            self.status_display.configure(text="Đang nhận diện huyệt đạo...")
            self.detect_button.state(['disabled'])
            
            # Bắt đầu camera nếu chưa chạy
            if not self.camera_thread or not self.camera_thread.is_alive():
                self.camera_thread = CameraThread(self.process_frame)
                self.camera_thread.start()

def create_splash_screen(parent):
    """Create a splash screen while the application loads"""
    splash = tk.Toplevel(parent)
    splash.title("")
    splash.geometry("640x480")
    splash.overrideredirect(True)  # Remove window decorations

    # Center splash screen
    center_window(splash)

    # Create content
    frame = ttk.Frame(splash, padding="20")
    frame.pack(fill='both', expand=True)

    # Add logo or title
    title = ttk.Label(frame, 
                     text="BMD Machine Control",
                     font=('Helvetica', 20, 'bold'))
    title.pack(pady=(50,20))

    # Add version
    version = ttk.Label(frame,
                       text="Version 3.5",
                       font=('Helvetica', 12))
    version.pack()

    # Add loading message
    loading = ttk.Label(frame,
                       text="Đang khởi động...",
                       font=('Helvetica', 10))
    loading.pack(pady=(50,0))

    # Add progress bar
    progress = ttk.Progressbar(frame, mode='indeterminate')
    progress.pack(fill='x', pady=(20,0))
    progress.start()

    return splash

def center_window(window):
    """Center a tkinter window on the screen"""
    window.update_idletasks()  # Ensure all geometry updates are processed
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')
    print(f"Window centered at: {x}, {y} with size: {width}x{height}")

def main():
    try:
        # Use ThemedTk instead of regular Tk for better looking widgets
        root = ThemedTk(theme="clam")
        root.configure(bg='#f0f0f0')

        # Withdraw main window while splash screen is active
        root.withdraw()

        # Set window size and prevent resizing
        root.geometry("1024x600")
        root.minsize(1024, 600)
        # root.maxsize(1024, 600)
        root.maxsize(1920, 1080)
        root.resizable(True, True)  # Disable window resizing
        root.update()  # Apply geometry settings immediately

        # Initialize application
        app = BMDMachineControl(root)

        # Create splash screen
        splash = create_splash_screen(root)

        # Center main window on screen
        center_window(root)

        # After splash screen is destroyed, show the main window
        root.after(2000, lambda: [splash.destroy(), root.deiconify()])

        # Start main loop
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    main()
