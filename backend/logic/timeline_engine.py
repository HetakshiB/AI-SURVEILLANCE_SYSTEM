import collections
import time
import os
import cv2

class TimelineEngine:
    def __init__(self, buffer_size=30, output_dir="outputs"):
        # buffer_size: number of frames to keep (approx 1-3 seconds depending on FPS)
        self.frame_buffer = collections.deque(maxlen=buffer_size)
        self.event_timeline = []
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def add_frame(self, frame):
        self.frame_buffer.append(frame.copy())

    def log_event(self, event_type, details=None):
        timestamp = time.strftime("%H:%M:%S")
        event = {
            "timestamp": timestamp,
            "event": event_type,
            "details": details
        }
        self.event_timeline.append(event)
        return event

    def save_event_clip(self, event_name):
        if not self.frame_buffer:
            return None
        
        filename = f"{event_name}_{int(time.time())}.mp4"
        path = os.path.join(self.output_dir, filename)
        
        h, w, _ = self.frame_buffer[0].shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(path, fourcc, 10.0, (w, h))
        
        for f in self.frame_buffer:
            out.write(f)
        out.release()
        return path

    def get_timeline(self, limit=10):
        return self.event_timeline[-limit:]
    
    def clear_timeline(self):
        self.event_timeline = []
