from ultralytics import YOLO
import cv2
import face_recognition
import os
import numpy as np
import mediapipe as mp

# ================== LOAD MODELS ==================
weapon_model = YOLO("best.pt")        # your trained model
person_model = YOLO("yolov8n.pt")     # pretrained

# ================== FACE DATA ==================
BASE_PATH = "criminal-dataset"
TOLERANCE = 0.5

known_encodings = []
known_names = []

for person in os.listdir(BASE_PATH):
    person_path = os.path.join(BASE_PATH, person)

    for file in os.listdir(person_path):
        img_path = os.path.join(person_path, file)

        img = face_recognition.load_image_file(img_path)
        enc = face_recognition.face_encodings(img)

        if enc:
            known_encodings.append(enc[0])
            known_names.append(person)

print("Face encodings loaded!")

# ================== MEDIAPIPE POSE ==================
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# ================== UTILITY FUNCTIONS ==================
def get_center(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2)//2, (y1 + y2)//2)

def distance(p1, p2):
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5

# ================== START CAMERA ==================
cap = cv2.VideoCapture(0)

cv2.namedWindow("AI Surveillance System", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("AI Surveillance System", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    persons = []
    weapons = []
    criminal_detected = False

    # ================== PERSON DETECTION ==================
    person_results = person_model(frame, conf=0.5)

    for r in person_results:
        if r.boxes is None:
            continue

        for box in r.boxes:
            cls = int(box.cls[0])

            if person_model.names[cls] != "person":
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            persons.append((x1, y1, x2, y2))

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.putText(frame, "Person", (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    # ================== WEAPON DETECTION ==================
    weapon_results = weapon_model(frame, conf=0.6, imgsz=640)

    for r in weapon_results:
        if r.boxes is None:
            continue

        for box in r.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if (x2-x1) < 60 or (y2-y1) < 60:
                continue

            label = weapon_model.names[cls]
            weapons.append((x1, y1, x2, y2))

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,0,255), 2)
            cv2.putText(frame, f"{label} {conf:.2f}",
                        (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

    # ================== FACE RECOGNITION ==================
    small_frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
    rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small)
    face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

    for (top, right, bottom, left), face_enc in zip(face_locations, face_encodings):

        distances = face_recognition.face_distance(known_encodings, face_enc)

        name = "Person"
        color = (0,255,0)

        if len(distances) > 0:
            best_idx = np.argmin(distances)

            if distances[best_idx] < TOLERANCE:
                name = f"{known_names[best_idx]} FOUND"
                color = (0,0,255)
                criminal_detected = True

        top *= 2; right *= 2; bottom *= 2; left *= 2

        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, name, (left, top-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # ================== POSE DETECTION ==================
    rgb_pose = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pose_result = pose.process(rgb_pose)

    if pose_result.pose_landmarks:
        for lm in pose_result.pose_landmarks.landmark:
            h, w, _ = frame.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (cx, cy), 2, (255, 0, 0), -1)

    # ================== SUSPICIOUS LOGIC ==================
    alert = "SAFE"

    if len(weapons) > 0 and len(persons) > 0:
        alert = "HIGH ALERT 🚨"

    elif criminal_detected:
        alert = "CRIMINAL DETECTED"

    elif pose_result.pose_landmarks:
        wrist = pose_result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]

        if wrist.y < 0.3:
            alert = "AGGRESSIVE POSTURE"

    elif len(persons) >= 2:
        c1 = get_center(persons[0])
        c2 = get_center(persons[1])

        if distance(c1, c2) < 150:
            alert = "SUSPICIOUS BEHAVIOR"

    elif len(weapons) > 0:
        alert = "WEAPON DETECTED"

    # ================== DISPLAY ALERT ==================
    color = (0,255,0)

    if "ALERT" in alert or "CRIMINAL" in alert:
        color = (0,0,255)

    cv2.putText(frame, alert, (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2, color, 3)

    cv2.imshow("AI Surveillance System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()