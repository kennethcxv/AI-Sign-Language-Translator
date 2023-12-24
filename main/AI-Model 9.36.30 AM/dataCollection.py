import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import math
import time

last_error_displayed = {
    "camera_error": 0,
    "aspect_ratio_error": 0,
    "close_to_camera_error": 0,
    "no_hand_detected_error": 0,
    "general_error": 0
}


def can_display_error(error_key):
    current_time = time.time()
    if current_time - last_error_displayed[error_key] >= 5:
        last_error_displayed[error_key] = current_time
        return True
    return False


cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1)

offset = 20
imgSize = 300

folder = "Data/Z"
counter = 0

while True:
    try:
        success, img = cap.read()
        hands, img = detector.findHands(img)
        imgOutput = img.copy()
        img = cv2.flip(img, 1)
        if not success:
            if can_display_error("camera_error"):
                print("Failed to read frame from camera. Please check your camera connection.")
            continue

        key = cv2.waitKey(1)
        if key != -1:
            break

        if hands:
            hand = hands[0]
            x, y, w, h = hand['bbox']

            imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
            imgCrop = img[y - offset:y + h + offset, x - offset:x + w + offset]

            imgCropShape = imgCrop.shape
            aspectRatio = h / w

            if aspectRatio > 1:
                k = imgSize / h
                wCal = math.ceil(k * w)
                imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                imgResizeShape = imgResize.shape
                wGap = math.ceil((imgSize - wCal) / 2)
                imgWhite[:, wGap:wCal + wGap] = imgResize
            else:
                k = imgSize / w
                hCal = math.ceil(k * h)
                imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                imgResizeShape = imgResize.shape
                hGap = math.ceil((imgSize - hCal) / 2)
                imgWhite[hGap:hCal + hGap, :] = imgResize

            cv2.imshow("ImageCrop", imgCrop)
            cv2.imshow("ImageWhite", imgWhite)

        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        if key == ord("s"):
            counter += 1
            cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', imgWhite)
            print(counter)

    except Exception as e:
        if can_display_error("general_error"):
            print(f"An error occurred: {e}")
            print("Please ensure your hand is visible and not too close to the camera.")
        continue

    if not hands:
        if can_display_error("no_hand_detected_error"):
            print("No hand detected. Please place your hand inside the frame.")
