from flask import Flask, render_template, jsonify, request
from google.cloud import texttospeech
import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import math
import time
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"

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
detector = HandDetector(maxHands=2)
classifier = Classifier("Model/keras_model.h5", "Model/labels.txt")

offset = 20
imgSize = 300

last_print_time = 0
counter = 0
last_capture_time = 0
capture_interval = 2

labels = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W",
          "X", "Y", "Z"]
captured_chars = []

# app = Flask(__name__)
#
#
# @app.route('/')
# def index():
#     return render_template('index.html')
#
#
# @app.route('/get_captured_chars', methods=['GET'])
# def get_captured_chars():
#     return jsonify({"captured_chars": captured_chars})
#
#
# @app.route('/get_audio', methods=['GET'])
# def get_audio():
#     return send_file("captured_audio.mp3", as_attachment=True)


# if __name__ == "__main__":
#     app.run(debug=True)

while True:
    try:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        if not success:
            if can_display_error("camera_error"):
                print("Failed to read frame from camera. Please check your camera connection.")
            continue

        imgOutput = img.copy()
        hands, img = detector.findHands(img)

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
                wGap = math.ceil((imgSize - wCal) / 2)
                imgWhite[:, wGap:wCal + wGap] = imgResize
                prediction, index = classifier.getPrediction(imgWhite, draw=False)
            else:
                k = imgSize / w
                hCal = math.ceil(k * h)
                imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                hGap = math.ceil((imgSize - hCal) / 2)
                imgWhite[hGap:hCal + hGap, :] = imgResize
                prediction, index = classifier.getPrediction(imgWhite, draw=False)

            current_time = time.time()
            if current_time - last_capture_time >= capture_interval:
                captured_char = labels[index]
                if not captured_chars or (captured_chars and captured_chars[-1] != captured_char):
                    captured_chars.append(captured_char)
                    print(f"{captured_chars}")
                    last_capture_time = current_time

            cv2.rectangle(imgOutput, (x - offset, y - offset - 50), (x - offset + 90, y - offset - 50 + 50),(0, 245, 0), cv2.FILLED)
            cv2.putText(imgOutput, labels[index], (x, y - 25), cv2.FONT_HERSHEY_COMPLEX, 1.7, (255, 255, 255), 2)
            cv2.rectangle(imgOutput, (x - offset, y - offset), (x + w + offset, y + h + offset), (0, 245, 0), 4)

            cv2.imshow("ImageCrop", imgCrop)
            cv2.imshow("ImageWhite", imgWhite)

        cv2.imshow("Image", imgOutput)
        cv2.waitKey(1)

    except Exception as e:
        if can_display_error("general_error"):
            print(f"An error occurred: {e}")
            print("Please ensure your hand is visible and not too close to the camera.")
        continue

    if not hands:
        if can_display_error("no_hand_detected_error"):
            print("No hand detected. Please place your hand inside the frame.")

if captured_chars:
    tts_text = ' '.join(captured_chars)
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=tts_text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        # name="en-US-Wavenet-F",
        ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open("captured_audio.mp3", "wb") as out:
        out.write(response.audio_content)
        print("Audio content written to file 'captured_audio.mp3'")

    os.system("afplay captured_audio.mp3")

