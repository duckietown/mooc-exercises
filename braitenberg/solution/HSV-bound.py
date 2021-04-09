import cv2
import numpy as np
import duckietown_code_utils as dcu
import sys
import time


def nothing(x):
    pass


# # Open the camera
# cap = cv2.VideoCapture(0)

# Create a window
cv2.namedWindow("image")

# create trackbars for color change
cv2.createTrackbar("lowH", "image", 0, 179, nothing)
cv2.createTrackbar("highH", "image", 179, 179, nothing)

cv2.createTrackbar("lowS", "image", 0, 255, nothing)
cv2.createTrackbar("highS", "image", 255, 255, nothing)

cv2.createTrackbar("lowV", "image", 0, 255, nothing)
cv2.createTrackbar("highV", "image", 255, 255, nothing)

frame0 = dcu.image_cv_from_jpg_fn(sys.argv[1])
lastL = np.array([0, 0, 0])
lastU = np.array([0, 0, 0])

while True:
    frame = frame0
    # get current positions of the trackbars
    ilowH = cv2.getTrackbarPos("lowH", "image")
    ihighH = cv2.getTrackbarPos("highH", "image")
    ilowS = cv2.getTrackbarPos("lowS", "image")
    ihighS = cv2.getTrackbarPos("highS", "image")
    ilowV = cv2.getTrackbarPos("lowV", "image")
    ihighV = cv2.getTrackbarPos("highV", "image")

    # convert color to hsv because it is easy to track colors in this color model
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_hsv = np.array([ilowH, ilowS, ilowV])
    higher_hsv = np.array([ihighH, ihighS, ihighV])
    if not np.allclose(lastL, lower_hsv) or not np.allclose(lastU, higher_hsv):

        print(f"lower {lower_hsv} upper {higher_hsv}")
        lastL = lower_hsv
        lastU = higher_hsv

    # Apply the cv2.inrange method to create a mask
    mask = cv2.inRange(hsv, lower_hsv, higher_hsv)
    # Apply the mask on the image to extract the original color
    frame = cv2.bitwise_and(frame, frame, mask=mask)
    cv2.imshow("image", frame)
    # Press q to exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
