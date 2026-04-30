# AI-SURVEILLANCE SYSTEM

A professional, modular AI-powered surveillance dashboard featuring multi-model detection, behavioral intelligence, and a real-time event timeline. This system is designed to identify weapons, recognize criminals, analyze postures, and track suspicious activities in real-time.

## Key Features

### Advanced Detection
- **Weapon Detection**: Custom-trained YOLO model (best.pt) to identify firearms and cold weapons.
- **Person Tracking**: High-performance YOLOv8 for real-time person detection and localization.
- **Criminal Face Recognition**: Integrated face_recognition module to match faces against a known criminal database.
- **Behavioral Posture Analysis**: MediaPipe-powered skeleton tracking to identify aggressive postures (e.g., raised arms).

### Intelligence and Analytics
- **Behavioral Intelligence**: Automatically tracks repeat offenders and identifies peak activity hours.
- **Event Timeline Engine**: Maintains a chronological log of all detected events with frame buffering for incident review.
- **Live Analytics**: Real-time bar charts and line graphs showing activity trends and frequency.
- **HTML Reporting**: Generate and download professional HTML reports of all recorded incidents.

### Modern UI Dashboard (Streamlit)
- **Live Monitoring**: High-speed frame processing with visual bounding boxes and alert overlays.
- **Multi-Source Support**: 
  - Live Webcam Feed
  - Image Upload (Static Analysis)
  - Video Upload (Forensic Analysis)
- **Alert Panel**: Color-coded notifications (SAFE / WARNING / HIGH ALERT).
- **Snapshot Capture**: One-click button to save annotated evidence to the outputs/ folder.

---

## Technology Stack
- **Framework**: Streamlit (UI Dashboard)
- **AI Models**: YOLOv8 (Ultralytics), MediaPipe (Pose), face_recognition (Dlib)
- **Core Logic**: Python 3.10+
- **Computer Vision**: OpenCV, NumPy, Pillow
- **Storage**: JSON-based incident logging

---

## Project Structure
```text
AI_SURVELLIENCE/
├── backend/
│   ├── detection/          # YOLO, Face, and Pose modules
│   ├── logic/              # Alert Engine, Behavior Analysis, Timeline
│   └── storage/            # Database and Persistence
├── ui/
│   └── app.py              # Main Streamlit Dashboard
├── scripts/                # Development and testing utilities
├── outputs/                # Saved incident frames and clips
├── assets/                 # Static assets and icons
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

---

## Installation and Setup

### 1. Prerequisites
- Python 3.10 or higher
- Webcam (for live monitoring)

### 2. Clone and Initialize
```powershell
# Activate your virtual environment
.\venv310\Scripts\Activate.ps1

# Install dependencies
python -m pip install -r requirements.txt
```

### 3. Run the System
```powershell
streamlit run ui/app.py
```

---

## How to Use
1. **Launch**: Start the dashboard using the command above.
2. **Select Source**: Use the sidebar to choose between **Webcam**, **Image**, or **Video**.
3. **Configure**: Toggle **Face Recognition** or **Pose Detection** as needed.
4. **Start**: Click **"Start System"** to begin real-time monitoring.
5. **Monitor**: Watch the live feed for alerts. Suspicious events will automatically appear in the **Event Timeline**.
6. **Analyze**: Review the **Peak Hours** and **Repeat Offenders** sections for long-term intelligence.

---

## License
This project is for educational and security research purposes.

---

