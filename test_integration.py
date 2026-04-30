import sys
import os

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd())))

try:
    from backend.detection.yolo_detector import YOLODetector
    from backend.detection.face_module import FaceRecognizer
    from backend.detection.pose_module import PoseEstimator
    from backend.logic.alert_engine import AlertEngine
    
    print("Imports successful!")
    
    # Test initialization
    yolo = YOLODetector(weapon_model_path="best.pt", person_model_path="yolov8n.pt")
    print("YOLO models loaded!")
    
    face = FaceRecognizer(dataset_path="criminal-dataset")
    print("Face recognizer loaded!")
    
    pose = PoseEstimator()
    print("Pose estimator loaded!")
    
    alert = AlertEngine()
    print("Alert engine loaded!")
    
    print("All modules initialized correctly.")

except Exception as e:
    print(f"Integration failed: {e}")
    sys.exit(1)
