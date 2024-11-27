import tkinter as tk
from tkinter import ttk
import cv2
from ultralytics import YOLO
import time
import numpy as np
from PIL import Image, ImageTk
import torch

class PoseDetectionApp:
    def __init__(self, window):
        self.window = window
        self.window.title("YOLO Pose Detection")
        self.model = YOLO('/home/ubuntu/Coding/swork/bmd-v3.5/models/best-640-100eps.pt')
        self.cap = cv2.VideoCapture('/home/ubuntu/Coding/swork/bmd-v3.5/video_test/1.mp4')
        
        self.frame_label = ttk.Label(window)
        self.frame_label.pack(pady=10)
        
        self.detect_button = ttk.Button(window, text="Nhận diện", command=self.start_detection)
        self.detect_button.pack(pady=5)
        
        self.is_detecting = False
        self.best_frame = None
        self.best_confidence = 0
        self.best_keypoints = None
        
    def start_detection(self):
        self.is_detecting = True
        self.best_confidence = 0
        self.best_frame = None
        self.best_keypoints = None
        
        start_time = time.time()
        
        while time.time() - start_time < 5:
            ret, frame = self.cap.read()
            if not ret:
                break
                
            results = self.model(frame, verbose=False)
            
            for result in results:
                if result.keypoints is not None:
                    conf = result.boxes.conf
                    
                    if len(conf) > 0:
                        max_conf = float(conf.max())
                        if max_conf > self.best_confidence:
                            self.best_confidence = max_conf
                            self.best_frame = frame.copy()
                            
                            best_idx = int(conf.argmax())
                            self.best_keypoints = result.keypoints[best_idx].data
            
            self.window.update()
            
        self.is_detecting = False
        self.display_best_result()
        
    def display_best_result(self):
        if self.best_frame is not None and self.best_keypoints is not None:
            frame = self.best_frame.copy()
            kpts = self.best_keypoints.cpu().numpy()
            
            for i in range(kpts.shape[1]):
                x, y = int(kpts[0, i, 0]), int(kpts[0, i, 1])
                if x > 0 and y > 0:
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            photo = ImageTk.PhotoImage(image=pil_image)
            
            self.frame_label.configure(image=photo)
            self.frame_label.image = photo
            
            print("\nTọa độ các keypoint:")
            keypoint_names = [
                "nose", "left_eye", "right_eye", "left_ear", "right_ear",
                "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
                "left_wrist", "right_wrist", "left_hip", "right_hip",
                "left_knee", "right_knee", "left_ankle", "right_ankle"
            ]
            
            for i, name in enumerate(keypoint_names):
                x, y = int(kpts[0, i, 0]), int(kpts[0, i, 1])
                if x > 0 and y > 0:
                    print(f"{name}: ({x}, {y})")
    
    def __del__(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = PoseDetectionApp(root)
    root.mainloop()