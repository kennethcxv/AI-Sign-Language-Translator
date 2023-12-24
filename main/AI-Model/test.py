from flask import Flask, render_template, Response, send_file, jsonify, request
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
from google.cloud import texttospeech
from threading import Thread
import numpy as np
import time
import math
import cv2
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"
app = Flask(__name__)

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
running = True
capture_enabled = True
captured_chars = []

frame_to_stream = np.zeros((720, 1280, 3), dtype=np.uint8)

thread = None
labels = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
          "W", "X", "Y"]

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


@app.route('/')
def index():
    global thread
    if thread is None:
        thread = Thread(target=run_ai)
        thread.start()
    return render_template('translator.html')


@app.route('/video')
def video():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/audio')
def audio():
    return send_file("captured_audio.mp3", mimetype='audio/mp3')


@app.route('/get_captured_chars')
def get_captured_chars():
    global captured_chars
    return jsonify({"captured_chars": ' '.join(captured_chars)})


@app.route('/keypress', methods=['POST'])
def keypress():
    key = request.form.get('key')
    if key == 'q':
        shutdown_server()
        return 'Server shutting down...'
    return 'Key not recognized'


@app.route('/generate_audio', methods=['POST'])
def generate_and_get_audio():
    generate_audio()
    return jsonify({"status": "Audio generated successfully"})


def gen_frames():
    # global frame_to_stream
    while True:
        if frame_to_stream is not None:
            ret, buffer = cv2.imencode('.jpg', frame_to_stream)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def run_ai():
    global captured_char
    global running
    global capture_enabled
    offset = 20
    imgSize = 300
    last_capture_time = 0
    capture_interval = 2

    detector = HandDetector(maxHands=2)
    classifier = Classifier("Model/keras_model.h5", "Model/labels.txt")

    try:
        while running:
            if capture_enabled:
                success, img = cap.read()
                img = cv2.flip(img, 1)
                if not success:
                    if can_display_error("camera_error"):
                        print("Failed to read frame from camera. Please check your camera connection.")
                    continue

                hands, img = detector.findHands(img)
                if hands:
                    hand = hands[0]
                    x, y, w, h = hand['bbox']
                    imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
                    imgCrop = img[y - offset:y + h + offset, x - offset:x + w + offset]
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

                    cv2.rectangle(img, (x - offset, y - offset - 50), (x - offset + 90, y - offset - 50 + 50), (0, 245, 0),
                                  cv2.FILLED)
                    # cv2.putText(img, labels[index], (x, y - 25), cv2.FONT_HERSHEY_SIMPLEX, 1.7, (255, 255, 255), 2,
                    #             cv2.LINE_AA)
                    cv2.rectangle(img, (x - offset, y - offset), (x + w + offset, y + h + offset), (0, 245, 0), 4)

                    global frame_to_stream
                    frame_to_stream = img

                    current_time = time.time()
                    if current_time - last_capture_time >= capture_interval:
                        captured_char = labels[index]
                        if not captured_chars or (captured_chars and captured_chars[-1] != captured_char):
                            captured_chars.append(captured_char)
                            last_capture_time = current_time

                if not hands:
                    if can_display_error("no_hand_detected_error"):
                        print("No hand detected. Please place your hand inside the frame.")
                    continue

    except Exception as e:
        if can_display_error("general_error"):
            print(f"An error occurred: {e}")
            print("Please ensure your hand is visible and not too close to the camera.")

    except KeyboardInterrupt:
        print("Program interrupted by user. Generating audio...")
        generate_audio()


def generate_audio():
    if captured_chars:
        tts_text = ' '.join(captured_chars)
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=tts_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
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


def shutdown_server():
    global running
    global capture_enabled  # Add this line
    capture_enabled = False  # Stop capturing characters
    generate_audio()  # Generate audio immediately when shutdown is called
    running = False


if __name__ == '__main__':
    app.run(debug=True)
