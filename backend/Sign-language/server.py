from flask import Flask, Response, jsonify
import cv2
import numpy as np
import mediapipe as mp
from tensorflow.keras.models import model_from_json

# Initialize Flask app
app = Flask(__name__)

# Load the model architecture from model_json
with open('model_json', 'r') as json_file:
    model_json = json_file.read()
model = model_from_json(model_json)

# Load weights into the model from .h5 file
model.load_weights('model_json.weights.h5')

# Initialize video capture
cap = cv2.VideoCapture(0)

# MediaPipe setup for hand detection
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

# Dictionary of labels
labels_dict = {0: 'A', 1: 'B', 2: 'L'}

# Route for video feed
@app.route('/')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Function to generate video frames
def gen_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Route for predictions
@app.route('/', methods=['GET'])
def predict():
    success, frame = cap.read()
    if not success:
        return jsonify({'prediction': 'No frame captured'}), 500

    data_aux = []
    x_, y_ = [], []

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                x_.append(x)
                y_.append(y)
            
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                data_aux.append(x - min(x_))
                data_aux.append(y - min(y_))

        prediction = model.predict([np.asarray(data_aux)])
        predicted_character = labels_dict[int(prediction[0])]

        return jsonify({'prediction': predicted_character})

    return jsonify({'prediction': 'No hand detected'})

# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=8080)
