import cv2

def check_cameras():
    num_cameras = 0
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Camera {i} is available")
            num_cameras += 1
        else:
            print(f"Camera {i} is not available")
        cap.release()

    if num_cameras == 0:
        print("No cameras are available")

check_cameras()