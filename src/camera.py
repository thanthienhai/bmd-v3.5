# Code to access the camera
import cv2

def get_camera():
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        raise Exception("Error: Could not open camera.")
    
    return cap

def capture_frame(cap):
    ret, frame = cap.read()
    
    if not ret:
        raise Exception("Error: Failed to capture image.")
    
    return frame

def release_camera(cap):
    cap.release()
