import face_recognition
import os
import numpy as np
import cv2

class FaceRecognizer:
    def __init__(self, dataset_path="criminal-dataset", tolerance=0.5):
        self.dataset_path = dataset_path
        self.tolerance = tolerance
        self.known_encodings = []
        self.known_names = []
        self._load_dataset()

    def _load_dataset(self):
        if not os.path.exists(self.dataset_path):
            print(f"Warning: Dataset path {self.dataset_path} not found.")
            return

        for person in os.listdir(self.dataset_path):
            person_path = os.path.join(self.dataset_path, person)
            if not os.path.isdir(person_path):
                continue

            for file in os.listdir(person_path):
                img_path = os.path.join(person_path, file)
                try:
                    img = face_recognition.load_image_file(img_path)
                    enc = face_recognition.face_encodings(img)
                    if enc:
                        self.known_encodings.append(enc[0])
                        self.known_names.append(person)
                except Exception as e:
                    print(f"Error loading {img_path}: {e}")
        print(f"Loaded {len(self.known_encodings)} face encodings.")

    def recognize_faces(self, frame):
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small)
        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

        detections = []
        criminal_detected = False

        for (top, right, bottom, left), face_enc in zip(face_locations, face_encodings):
            name = "Person"
            is_criminal = False
            
            if self.known_encodings:
                distances = face_recognition.face_distance(self.known_encodings, face_enc)
                if len(distances) > 0:
                    best_idx = np.argmin(distances)
                    if distances[best_idx] < self.tolerance:
                        name = self.known_names[best_idx]
                        is_criminal = True
                        criminal_detected = True

            # Scale back up face locations
            detections.append({
                "box": (top * 2, right * 2, bottom * 2, left * 2),
                "name": name,
                "is_criminal": is_criminal
            })

        return detections, criminal_detected
