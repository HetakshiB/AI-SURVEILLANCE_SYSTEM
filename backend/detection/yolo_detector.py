from ultralytics import YOLO
import cv2

class YOLODetector:
    def __init__(self, weapon_model_path="best.pt", person_model_path="yolov8n.pt"):
        self.weapon_model = YOLO(weapon_model_path)
        self.person_model = YOLO(person_model_path)
        self.person_class_id = 0 # Assuming 'person' is class 0 in yolov8n

    def detect_persons(self, frame, conf=0.5):
        results = self.person_model(frame, conf=conf, verbose=False)
        persons = []
        for r in results:
            if r.boxes is None:
                continue
            for box in r.boxes:
                cls = int(box.cls[0])
                if self.person_model.names[cls] != "person":
                    continue
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                persons.append((x1, y1, x2, y2))
        return persons

    def detect_weapons(self, frame, conf=0.6, min_size=60):
        results = self.weapon_model(frame, conf=conf, imgsz=640, verbose=False)
        weapons = []
        for r in results:
            if r.boxes is None:
                continue
            for box in r.boxes:
                cls = int(box.cls[0])
                conf_val = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                if (x2 - x1) < min_size or (y2 - y1) < min_size:
                    continue
                
                label = self.weapon_model.names[cls]
                weapons.append({
                    "box": (x1, y1, x2, y2),
                    "label": label,
                    "conf": conf_val
                })
        return weapons
