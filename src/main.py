# Entry point for the application
import cv2
from camera import get_camera, capture_frame, release_camera
from processing import convert_to_grayscale, apply_canny_edge_detection
from communication import RaspberryPiI2C
import time

def main():
    cap = get_camera()
    i2c = RaspberryPiI2C(address=0x08)  # I2C address of your microcontroller
    
    while True:
        try:
            # Capture frame
            frame = capture_frame(cap)
            gray_frame = convert_to_grayscale(frame)
            edges = apply_canny_edge_detection(gray_frame)
            
            # Send a signal to the microcontroller (example: send 1 when edges detected)
            if edges is not None:
                i2c.write_data(1)  # Example data to microcontroller
            
            # Read data from microcontroller (example: check if a flag is returned)
            microcontroller_data = i2c.read_data()
            if microcontroller_data == 1:
                print("Microcontroller sent a response.")
            
            # Display frames
            cv2.imshow('Original Frame', frame)
            cv2.imshow('Edge Detection', edges)

            # Exit when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        except Exception as e:
            print(e)
            break

    # Release resources
    release_camera(cap)
    i2c.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
