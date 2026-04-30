import cv2
import mediapipe as mp

class PoseEstimator:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.pose.process(rgb_frame)
        return result

    def check_aggressive_posture(self, pose_result):
        if not pose_result or not pose_result.pose_landmarks:
            return False
        
        # Simple rule: right wrist above a certain height (y < 0.3)
        wrist = pose_result.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
        if wrist.y < 0.3:
            return True
        return False

    def draw_landmarks(self, frame, pose_result):
        if pose_result and pose_result.pose_landmarks:
            h, w, _ = frame.shape
            for lm in pose_result.pose_landmarks.landmark:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 2, (255, 0, 0), -1)
        return frame
