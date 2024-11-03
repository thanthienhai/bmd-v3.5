import sys
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
from ultralytics import YOLO
from ttkthemes import ThemedTk

class CameraThread(threading.Thread):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.running = False
        self.camera_id = 0

    def run(self):
        # cap = cv2.VideoCapture(self.camera_id)
        cap = cv2.VideoCapture('/dev/video4') 
        # video_path = 'video_test/video.mp4'
        # cap = cv2.VideoCapture(video_path)
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
        self.root.geometry("640x480")
        
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
        self.massage_tab = ttk.Frame(self.notebook, padding="5")
        self.routine_tab = ttk.Frame(self.notebook, padding="5")
        self.settings_tab = ttk.Frame(self.notebook, padding="5")
        
        self.notebook.add(self.massage_tab, text=" Massage bàn chân ")
        self.notebook.add(self.routine_tab, text=" Tạo bài bấm huyệt ")
        self.notebook.add(self.settings_tab, text=" Cài đặt ")
        
        self.setup_massage_tab()
        self.setup_routine_tab()
        self.setup_settings_tab()
        
        self.camera_thread = CameraThread(self.process_frame)
        
        # Add status bar
        self.setup_status_bar()

    # def configure_styles(self):
    #     # Configure colors
    #     primary_color = "#2196F3"  # Material Blue
    #     secondary_color = "#FFC107"  # Material Amber
    #     success_color = "#4CAF50"  # Material Green
    #     danger_color = "#F44336"  # Material Red
        
    #     # Tab style
    #     self.style.configure('TNotebook.Tab', padding=[12, 8], font=('Helvetica', 10))
    #     self.style.map('TNotebook.Tab',
    #                   background=[('selected', primary_color), ('!selected', '#f0f0f0')],
    #                   foreground=[('selected', 'white'), ('!selected', 'black')])
        
    #     # Button styles
    #     self.style.configure('Primary.TButton',
    #                        padding=[20, 10],
    #                        font=('Helvetica', 10, 'bold'))
    #     self.style.map('Primary.TButton',
    #                   background=[('pressed', primary_color), ('active', primary_color)],
    #                   foreground=[('pressed', 'white'), ('active', 'white')])
        
    #     # Success button style
    #     self.style.configure('Success.TButton',
    #                        padding=[20, 10],
    #                        font=('Helvetica', 10, 'bold'))
    #     self.style.map('Success.TButton',
    #                   background=[('pressed', success_color), ('active', success_color)],
    #                   foreground=[('pressed', 'white'), ('active', 'white')])
        
    #     # Danger button style
    #     self.style.configure('Danger.TButton',
    #                        padding=[20, 10],
    #                        font=('Helvetica', 10, 'bold'))
    #     self.style.map('Danger.TButton',
    #                   background=[('pressed', danger_color), ('active', danger_color)],
    #                   foreground=[('pressed', 'white'), ('active', 'white')])
        
    #     # Label styles
    #     self.style.configure('Title.TLabel',
    #                        font=('Helvetica', 16, 'bold'),
    #                        padding=[0, 10])
        
    #     self.style.configure('Status.TLabel',
    #                        font=('Helvetica', 10),
    #                        padding=[5, 5])

    # def setup_massage_tab(self):
    #     # Title
    #     title = ttk.Label(self.massage_tab, 
    #                      text="Điều khiển massage bấm huyệt",
    #                      style='Title.TLabel')
    #     title.pack(fill='x', pady=(0, 20))
        
    #     # Create main content frame with two columns
    #     content_frame = ttk.Frame(self.massage_tab)
    #     content_frame.pack(fill='both', expand=True)
        
    #     # Left column - Display
    #     display_frame = ttk.LabelFrame(content_frame, text="Hiển thị camera", padding="5")
    #     display_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
    #     # Camera displays with borders and shadows
    #     self.left_display = ttk.Label(display_frame, relief='solid', borderwidth=1)
    #     self.left_display.pack(fill='both', expand=True, padx=5, pady=5)
        
    #     self.right_display = ttk.Label(display_frame, relief='solid', borderwidth=1)
    #     self.right_display.pack(fill='both', expand=True, padx=5, pady=5)
        
    #     # Right column - Controls
    #     control_frame = ttk.LabelFrame(content_frame, text="Điều khiển", padding="5")
    #     control_frame.pack(side='right', fill='y', padx=(10, 0))
        
    #     # Routine selection with better styling
    #     ttk.Label(control_frame, text="Chọn bài bấm huyệt:",
    #              font=('Helvetica', 10, 'bold')).pack(fill='x', pady=(0, 5))
        
    #     routines = ["Sốt, co giật", "Stress", "Thoát vị đĩa đệm", 
    #                "Bổ thận tráng dương", "Nâng cao sức khỏe"]
    #     self.routine_var = tk.StringVar()
    #     routine_combo = ttk.Combobox(control_frame, 
    #                                textvariable=self.routine_var,
    #                                values=routines,
    #                                width=30)
    #     routine_combo.pack(fill='x', pady=(0, 20))
        
    #     # Medicine control group
    #     medicine_frame = ttk.LabelFrame(control_frame, text="Điều khiển dẫn dược", padding="5")
    #     medicine_frame.pack(fill='x', pady=(0, 10))
        
    #     self.btn_on_medicine = CustomButton(medicine_frame, 
    #                                       text="Bật dẫn dược",
    #                                       style='Success.TButton',
    #                                       command=self.toggle_medicine)
    #     self.btn_on_medicine.pack(fill='x', pady=2)
        
    #     self.btn_off_medicine = CustomButton(medicine_frame, 
    #                                        text="Tắt dẫn dược",
    #                                        style='Danger.TButton',
    #                                        command=self.toggle_medicine)
    #     self.btn_off_medicine.pack(fill='x', pady=2)
        
    #     # Herb control group
    #     herb_frame = ttk.LabelFrame(control_frame, text="Điều khiển dược liệu", padding="10")
    #     herb_frame.pack(fill='x', pady=(0, 10))
        
    #     self.btn_on_herb = CustomButton(herb_frame, 
    #                                   text="Đốt dược liệu",
    #                                   style='Success.TButton',
    #                                   command=self.toggle_herb)
    #     self.btn_on_herb.pack(fill='x', pady=2)
        
    #     self.btn_off_herb = CustomButton(herb_frame, 
    #                                    text="Tắt đốt dược liệu",
    #                                    style='Danger.TButton',
    #                                    command=self.toggle_herb)
    #     self.btn_off_herb.pack(fill='x', pady=2)
        
    #     # Main control buttons
    #     control_buttons_frame = ttk.Frame(control_frame)
    #     control_buttons_frame.pack(fill='x', pady=20)
        
    #     self.start_button = CustomButton(control_buttons_frame, 
    #                                    text="Bắt đầu bấm huyệt",
    #                                    style='Success.TButton',
    #                                    command=self.start_massage)
    #     self.start_button.pack(fill='x', pady=2)
        
    #     self.stop_button = CustomButton(control_buttons_frame, 
    #                                   text="Dừng máy",
    #                                   style='Danger.TButton',
    #                                   command=self.stop_massage)
    #     self.stop_button.pack(fill='x', pady=2)
    
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
                # Adjust base size according to window width
                base_size = max(8, min(12, window_width // 80))  # Responsive font size
                button_padding = max(6, min(15, window_width // 100))  # Responsive padding
                
                # Update button styles
                self.style.configure('Primary.TButton',
                                padding=[button_padding * 2, button_padding],
                                font=('Helvetica', base_size, 'bold'))
                
                self.style.configure('Success.TButton',
                                padding=[button_padding * 2, button_padding],
                                font=('Helvetica', base_size, 'bold'))
                
                self.style.configure('Danger.TButton',
                                padding=[button_padding * 2, button_padding],
                                font=('Helvetica', base_size, 'bold'))
                
                # Update label styles
                self.style.configure('Title.TLabel',
                                font=('Helvetica', base_size + 4, 'bold'),
                                padding=[0, button_padding])
                
                self.style.configure('Status.TLabel',
                                font=('Helvetica', base_size - 2),
                                padding=[button_padding//2, button_padding//2])
        
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
        
        # Create a frame for the left side (70% of width)
        left_main_frame = ttk.Frame(content_frame)
        left_main_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Left column - Display frame (takes up available space)
        display_frame = ttk.LabelFrame(left_main_frame, text="Hiển thị camera", padding="5")
        display_frame.pack(fill='both', expand=True)
        
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
        control_frame.pack(side='right', fill='both', padx=(10, 0))
        
        # Make control frame elements expand horizontally
        control_frame.grid_columnconfigure(0, weight=1)
        
        # Routine selection with better styling
        ttk.Label(control_frame, text="Chọn bài bấm huyệt:",
                font=('Helvetica', 10, 'bold')).pack(fill='x', pady=(0, 5))
        
        routines = ["Sốt, co giật", "Stress", "Thoát vị đĩa đệm", 
                "Bổ thận tráng dương", "Nâng cao sức khỏe"]
        self.routine_var = tk.StringVar()
        routine_combo = ttk.Combobox(control_frame, 
                                textvariable=self.routine_var,
                                values=routines)
        routine_combo.pack(fill='x', pady=(0, 20))
        
        # Medicine control group
        medicine_frame = ttk.LabelFrame(control_frame, text="Điều khiển dẫn dược", padding="5")
        medicine_frame.pack(fill='x', pady=(0, 10))
        medicine_frame.grid_columnconfigure(0, weight=1)
        
        self.btn_on_medicine = CustomButton(medicine_frame, 
                                        text="Bật dẫn dược",
                                        style='Success.TButton',
                                        command=self.toggle_medicine)
        self.btn_on_medicine.pack(fill='x', pady=2)
        
        self.btn_off_medicine = CustomButton(medicine_frame, 
                                        text="Tắt dẫn dược",
                                        style='Danger.TButton',
                                        command=self.toggle_medicine)
        self.btn_off_medicine.pack(fill='x', pady=2)
        
        # Herb control group with grid layout
        herb_frame = ttk.LabelFrame(control_frame, text="Điều khiển dược liệu", padding="5")
        herb_frame.pack(fill='x', pady=(0, 10))
        herb_frame.grid_columnconfigure(0, weight=1)
        
        self.btn_on_herb = CustomButton(herb_frame, 
                                    text="Đốt dược liệu",
                                    style='Success.TButton',
                                    command=self.toggle_herb)
        self.btn_on_herb.pack(fill='x', pady=2)
        
        self.btn_off_herb = CustomButton(herb_frame, 
                                    text="Tắt đốt dược liệu",
                                    style='Danger.TButton',
                                    command=self.toggle_herb)
        self.btn_off_herb.pack(fill='x', pady=2)
        
        # Main control buttons with grid layout
        control_buttons_frame = ttk.Frame(control_frame)
        control_buttons_frame.pack(fill='x', pady=20)
        control_buttons_frame.grid_columnconfigure(0, weight=1)
        
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
            image = Image.fromarray(frame)
            photo = ImageTk.PhotoImage(image)
            self.left_display.configure(image=photo)
            self.left_display.image = photo

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
        # root.iconbitmap('path/to/your/icon.ico')
        
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

def create_splash_screen(parent):
    """Create a splash screen while the application loads"""
    splash = tk.Toplevel(parent)
    splash.title("")
    splash.geometry("400x300")
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
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

class FootAcupointDetector:
    """Placeholder class for foot acupoint detection"""
    def __init__(self, model_path):
        self.model = YOLO(model_path) if model_path else None

    def detect_acupoints(self, frame):
        """Detect acupoints in the given frame"""
        if self.model:
            # Add your actual detection logic here
            return []
        return []

    def visualize_keypoints(self, frame, keypoints):
        """Visualize detected keypoints on the frame"""
        if keypoints:
            for point in keypoints:
                # Add your visualization logic here
                pass
        return frame

if __name__ == "__main__":
    main()