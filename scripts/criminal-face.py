import face_recognition
import cv2
import os
import numpy as np

# ===== SETTINGS =====
BASE_PATH = "criminal-dataset"
TOLERANCE = 0.5   # lower = stricter (0.45–0.6 range)

known_encodings = []
known_names = []

# ===== LOAD AND ENCODE FACES =====
for person in os.listdir(BASE_PATH):
    person_path = os.path.join(BASE_PATH, person)

    for file in os.listdir(person_path):
        img_path = os.path.join(person_path, file)

        img = face_recognition.load_image_file(img_path)
        encodings = face_recognition.face_encodings(img)

        if encodings:
            known_encodings.append(encodings[0])
            known_names.append(person)

print(f"Loaded {len(known_encodings)} face encodings.")

# ===== START WEBCAM =====
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize for speed
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Detect faces
    face_locations = face_recognition.face_locations(rgb_small)
    face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

    for (top, right, bottom, left), face_enc in zip(face_locations, face_encodings):

        # Compare with known faces
        distances = face_recognition.face_distance(known_encodings, face_enc)

        name = "Person"
        color = (0, 255, 0)

        if len(distances) > 0:
            best_match_index = np.argmin(distances)
            best_distance = distances[best_match_index]

            if best_distance < TOLERANCE:
                name = f"{known_names[best_match_index]} FOUND"
                color = (0, 0, 255)

        # Scale back up face locations
        top *= 2
        right *= 2
        bottom *= 2
        left *= 2

        # Draw box
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

        # Draw label
        cv2.putText(frame,
                    name,
                    (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2)

    # Display
    cv2.imshow("Criminal Face Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()