# Image processing functions
import cv2

def convert_to_grayscale(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

def apply_canny_edge_detection(frame, low_threshold=100, high_threshold=200):
    return cv2.Canny(frame, low_threshold, high_threshold)
