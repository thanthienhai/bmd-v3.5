import cv2
import numpy as np

# Load the image
image = cv2.imread('/home/thanthien/Coding/bmd-v3.5/tests/images/e2bbe41183cb3a9563da.jpg')

# Step 1: Preprocessing
# Convert the image to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply Gaussian blur to smooth the image
blurred = cv2.GaussianBlur(gray, (5, 5), 0)

# Apply binary thresholding to create a binary image
_, thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY_INV)

# Step 2: Find the largest contour (which should be the foot)
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
largest_contour = max(contours, key=cv2.contourArea)

# Step 3: Draw the largest contour on the original image
cv2.drawContours(image, [largest_contour], -1, (0, 255, 0), 2)

# Step 4: Calculate key points (you can modify this to detect specific points)
x, y, w, h = cv2.boundingRect(largest_contour)

# For simplicity, let's mark a few key points: heel, toes, center
heel = (x + w // 2, y + h)
cv2.circle(image, heel, 5, (0, 0, 255), -1)

toes = (x + w // 2, y)
cv2.circle(image, toes, 5, (255, 0, 0), -1)

center = (x + w // 2, y + h // 2)
cv2.circle(image, center, 5, (0, 255, 0), -1)

# Resize the image to fit in a smaller window
# For example, resizing the image to 400x400 pixels
resized_image = cv2.resize(image, (400, 400))
resized_thresh = cv2.resize(thresh, (400, 400))

# Step 5: Create a fixed window and display the results
cv2.namedWindow('Resized Original Image', cv2.WINDOW_NORMAL)
cv2.namedWindow('Resized Threshold Image', cv2.WINDOW_NORMAL)

# Resize the window to a fixed size, for example, 500x500 pixels
cv2.resizeWindow('Resized Original Image', 500, 500)
cv2.resizeWindow('Resized Threshold Image', 500, 500)

# Show the resized images
cv2.imshow('Resized Original Image', resized_image)
cv2.imshow('Resized Threshold Image', resized_thresh)

while True:
    # Wait for a key press for 1 millisecond
    key = cv2.waitKey(1) & 0xFF
    
    # If the 'q' key is pressed, break the loop
    if key == ord('q'):
        print("Exiting the program...")
        break
    
    # If the 'ESC' key is pressed, break the loop (ESC key has the value 27)
    if key == 27:
        print("Exiting the program with ESC...")
        break

# Clean up: close all windows
cv2.destroyAllWindows()
