from ultralytics import YOLO
import cv2
from collections import deque, Counter

# ===== LOAD MODELS =====
weapon_model = YOLO("best.pt")        # your trained model
person_model = YOLO("yolov8n.pt")     # pretrained for person

# ===== WEBCAM =====
cap = cv2.VideoCapture(0)

# ===== TEMPORAL MEMORY =====
history = deque(maxlen=5)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # ===== PERSON DETECTION =====
    person_results = person_model(frame, conf=0.5)

    # ===== WEAPON DETECTION =====
    weapon_results = weapon_model(frame, conf=0.6, imgsz=640, max_det=10)

    current_labels = []

    # ===== DRAW PERSON BOXES (GREEN) =====
    for r in person_results:
        if r.boxes is None:
            continue

        for box in r.boxes:
            cls = int(box.cls[0])

            if person_model.names[cls] != "person":
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, "Person", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # ===== DRAW WEAPON BOXES (RED) =====
    for r in weapon_results:
        if r.boxes is None:
            continue

        for box in r.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # ===== FILTER SMALL BOXES (REDUCE FALSE POSITIVES) =====
            width = x2 - x1
            height = y2 - y1

            if width < 60 or height < 60:
                continue

            label = weapon_model.names[cls]
            current_labels.append(label)

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame, f"{label} {conf:.2f}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 0, 255), 2)

    # ===== TEMPORAL SMOOTHING =====
    if current_labels:
        history.extend(current_labels)

    if history:
        stable = Counter(history).most_common(1)[0][0]

        cv2.putText(frame,
                    f"Stable: {stable}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 255), 3)

    # ===== DISPLAY =====
    cv2.imshow("AI Surveillance System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()