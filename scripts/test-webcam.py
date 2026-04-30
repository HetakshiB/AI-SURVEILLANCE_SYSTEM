from ultralytics import YOLO
import cv2
from collections import deque, Counter

# Load trained model
model = YOLO("best.pt")

# Webcam
cap = cv2.VideoCapture(0)

# Store last few predictions for stability
history = deque(maxlen=5)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run detection with confidence threshold
    results = model(frame, conf=0.5, imgsz=640)

    current_labels = []

    for r in results:
     boxes = r.boxes

     if boxes is None:
        continue

     for box in boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])

        if conf < 0.4:
            continue

        label = model.names[cls]

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        # RED for weapon
        color = (0, 0, 255)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"{label} {conf:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, color, 2)

    # ===== TEMPORAL SMOOTHING =====
    if current_labels:
        history.extend(current_labels)

    if history:
        most_common = Counter(history).most_common(1)[0][0]

        # Display stable prediction
        cv2.putText(frame,
                    f"Stable: {most_common}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 255), 3)

    # Show frame
    cv2.imshow("AI Surveillance - Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()