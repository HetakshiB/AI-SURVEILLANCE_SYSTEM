import streamlit as st
import cv2
import numpy as np
import os
import sys
import time
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Add root directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.detection.yolo_detector import YOLODetector
from backend.detection.face_module import FaceRecognizer
from backend.detection.pose_module import PoseEstimator
from backend.logic.alert_engine import AlertEngine
from backend.logic.behavior_analysis import BehaviorAnalysis
from backend.logic.timeline_engine import TimelineEngine
from backend.logic.cooldown_manager import CooldownManager
from backend.logic.voice_engine import VoiceEngine
from backend.storage.database import Database
from backend.storage.report_generator import ReportGenerator

# Page Configuration
st.set_page_config(
    page_title="AI-SURVEILLANCE SYSTEM",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (Enterprise Dark Theme & Glassmorphism) ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background: radial-gradient(circle at top right, #0d1b2a, #000814);
        color: #e0e1dd;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(13, 27, 42, 0.8) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Card/Panel Styling */
    .glass-card {
        background: rgba(27, 38, 59, 0.4);
        backdrop-filter: blur(12px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    /* Metric Styling */
    [data-testid="stMetricValue"] {
        color: #00b4d8 !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Exo 2', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    /* Alert Banners */
    .alert-banner {
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 20px;
        animation: pulse 2s infinite;
    }
    .alert-critical { background: rgba(231, 76, 60, 0.2); border: 1px solid #e74c3c; color: #e74c3c; }
    .alert-warning { background: rgba(243, 156, 18, 0.2); border: 1px solid #f39c12; color: #f39c12; }
    .alert-safe { background: rgba(46, 204, 113, 0.1); border: 1px solid #2ecc71; color: #2ecc71; }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    /* Video Container */
    .video-container {
        border-radius: 20px;
        overflow: hidden;
        border: 2px solid rgba(0, 180, 216, 0.3);
        box-shadow: 0 0 20px rgba(0, 180, 216, 0.1);
    }
    
    /* Timeline Items */
    .timeline-item {
        padding: 10px;
        border-left: 2px solid #00b4d8;
        margin-bottom: 10px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 0 8px 8px 0;
    }
    .timeline-timestamp { font-size: 0.8em; color: #8d99ae; }
    .timeline-event { font-weight: 500; }
    
    /* Hide Streamlit default elements (Deploy button, Hamburger menu, etc.) */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# --- INITIALIZATION ---
@st.cache_resource
def init_backend():
    db = Database()
    yolo = YOLODetector()
    face = FaceRecognizer()
    pose = PoseEstimator()
    alert = AlertEngine()
    behavior = BehaviorAnalysis(db)
    timeline = TimelineEngine()
    cooldown = CooldownManager(default_cooldown=300)
    voice = VoiceEngine()
    return db, yolo, face, pose, alert, behavior, timeline, cooldown, voice

db, yolo, face, pose, alert_engine, behavior, timeline, cooldown_manager, voice_engine = init_backend()

# --- SYSTEM ACCESS (HACKATHON LOGIN) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<div class='glass-card' style='max-width: 500px; margin: 100px auto;'>", unsafe_allow_html=True)
    st.title("System Access")
    user_email = st.text_input("Administrator Email")
    user_phone = st.text_input("Emergency Contact Number")
    if st.button("Authorize System Access", use_container_width=True):
        if user_email and user_phone:
            st.session_state.authenticated = True
            st.session_state.admin_info = {"email": user_email, "phone": user_phone}
            st.rerun()
        else:
            st.error("Please provide both Email and Phone to proceed.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR (CONTROLS) ---
with st.sidebar:
    st.title("AI-SURVEILLANCE")
    st.subheader("System Configuration")
    
    with st.expander("Input Source", expanded=True):
        input_option = st.selectbox("Source Type", ["Live Webcam", "Upload Image", "Upload Video"], label_visibility="collapsed")
        if input_option == "Upload Image":
            uploaded_file = st.file_uploader("Choose Image", type=["jpg", "png", "jpeg"])
        elif input_option == "Upload Video":
            uploaded_video = st.file_uploader("Choose Video", type=["mp4", "avi", "mov"])
    
    with st.expander("Detection Modules", expanded=True):
        enable_face = st.toggle("Face Recognition", value=True)
        enable_pose = st.toggle("Posture Analysis", value=True)
        enable_voice = st.toggle("Audio Notifications", value=False)
    
    with st.expander("System Actions", expanded=True):
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            run_detection = st.button("Initialize", use_container_width=True)
        with col_btn2:
            save_frame = st.button("Capture", use_container_width=True)
        
        generate_report = st.button("Export HTML Report", use_container_width=True)
        clear_logs = st.button("Clear All Logs", use_container_width=True)

# --- MAIN LAYOUT ---
col_feed, col_stats = st.columns([1.6, 1])

with col_feed:
    st.markdown("<h2 style='margin-bottom: 20px;'>Live Security Monitoring</h2>", unsafe_allow_html=True)
    
    # System Status Indicator
    status_color = "#2ecc71" if 'cap' in locals() or run_detection else "#8d99ae"
    st.markdown(f"""
        <div style='display: flex; align-items: center; margin-bottom: 15px;'>
            <div style='width: 10px; height: 10px; background: {status_color}; border-radius: 50%; margin-right: 10px;'></div>
            <span style='font-size: 0.9em; color: #8d99ae;'>System Status: {'Active Monitoring' if run_detection else 'Standby'}</span>
        </div>
    """, unsafe_allow_html=True)
    
    frame_placeholder = st.empty()

with col_stats:
    st.markdown("<h2 style='margin-bottom: 20px;'>Intelligence Dashboard</h2>", unsafe_allow_html=True)
    
    # 1. Alert Status Card
    alert_placeholder = st.empty()
    
    # 2. Key Metrics Grid
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        total_alerts_metric = st.empty()
        weapons_metric = st.empty()
    with m_col2:
        criminals_metric = st.empty()
        suspicious_metric = st.empty()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 3. Charts
    tab1, tab2 = st.tabs(["Activity Trends", "Repeat Offenders"])
    
    with tab1:
        chart_placeholder = st.empty()
        peak_chart_placeholder = st.empty()
    
    with tab2:
        offenders_placeholder = st.empty()
    
    # 4. Event Timeline
    st.markdown("<h3>Event Timeline</h3>", unsafe_allow_html=True)
    timeline_container = st.container(height=300)
    with timeline_container:
        timeline_placeholder = st.empty()

# --- PROCESSING LOGIC ---
def process_frame(frame):
    persons = yolo.detect_persons(frame)
    weapons = yolo.detect_weapons(frame)
    
    criminal_detected = False
    face_detections = []
    if enable_face:
        face_detections, criminal_detected = face.recognize_faces(frame)
    
    pose_result = None
    aggressive_posture = False
    if enable_pose:
        pose_result = pose.process_frame(frame)
        aggressive_posture = pose.check_aggressive_posture(pose_result)
        frame = pose.draw_landmarks(frame, pose_result)

    alert_text, level = alert_engine.analyze(persons, weapons, criminal_detected, aggressive_posture)
    
    # Professional Overlay Drawing
    for (x1, y1, x2, y2) in persons:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
        cv2.putText(frame, "OBJECT: PERSON", (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
    
    for w in weapons:
        x1, y1, x2, y2 = w["box"]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(frame, f"THREAT: {w['label'].upper()}", (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        
    for f in face_detections:
        top, right, bottom, left = f["box"]
        color = (0, 0, 255) if f["is_criminal"] else (0, 255, 0)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 1)
        label = "CRIMINAL ID MATCH" if f["is_criminal"] else "PERSON ID"
        cv2.putText(frame, f"{label}: {f['name'].upper()}", (left, top - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    timeline.add_frame(frame)
    if level != "LOW":
        # Only log if cooldown period has passed for this specific alert
        if cooldown_manager.should_log(alert_text):
            if alert_text not in st.session_state.get('last_times', {}) or (time.time() - st.session_state.last_times[alert_text] > 60):
                if 'last_times' not in st.session_state: st.session_state.last_times = {}
                st.session_state.last_times[alert_text] = time.time()
                event = timeline.log_event(alert_text, {"level": level})
                db.log_incident(alert_text, level, {
                    "timestamp": event["timestamp"], 
                    "name": face_detections[0]['name'] if face_detections and face_detections[0]['is_criminal'] else None
                })
                # Voice Alert for Hackathon Demo
                if enable_voice and level == "HIGH":
                    voice_engine.speak(f"Security Alert. {alert_text}")

    return frame, alert_text, level

def update_dashboard_metrics():
    analytics = db.get_analytics()
    counts = analytics.get("activity_counts", {})
    
    total_alerts_metric.metric("Total Incidents", analytics.get("total_incidents", 0))
    weapons_metric.metric("Weapons Identified", counts.get("weapon_detected", 0) + counts.get("high_alert_🚨", 0))
    criminals_metric.metric("Criminal Hits", counts.get("criminal_detected", 0))
    suspicious_metric.metric("Suspicious Acts", counts.get("suspicious_behavior", 0) + counts.get("aggressive_posture", 0))

    if counts:
        fig = px.bar(
            x=list(counts.keys()), 
            y=list(counts.values()),
            title="Incident Distribution",
            template="plotly_dark",
            color_discrete_sequence=['#00b4d8']
        )
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=250, margin=dict(l=20, r=20, t=40, b=20))
        # Use a timestamp-based key to avoid duplicate element errors if needed, 
        # but here we use a fixed key as it's inside a placeholder.
        chart_placeholder.plotly_chart(fig, use_container_width=True, key=f"dist_chart_{st.session_state.frame_count}")

    peak_hours = behavior.get_peak_hours()
    if peak_hours:
        fig_peak = px.line(
            x=list(peak_hours.keys()), 
            y=list(peak_hours.values()),
            title="Activity Peak Hours",
            template="plotly_dark",
            markers=True
        )
        fig_peak.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=250, margin=dict(l=20, r=20, t=40, b=20))
        peak_chart_placeholder.plotly_chart(fig_peak, use_container_width=True, key=f"peak_chart_{st.session_state.frame_count}")

    offenders = behavior.get_repeat_offenders()
    if offenders:
        off_html = "<div class='glass-card' style='padding: 10px;'>"
        for name, count in offenders.items():
            off_html += f"<div style='display:flex; justify-content:space-between; margin-bottom:5px;'><span>{name.upper()}</span><span style='color:#e74c3c;'>{count} Sightings</span></div>"
        off_html += "</div>"
        offenders_placeholder.markdown(off_html, unsafe_allow_html=True)
    else:
        offenders_placeholder.info("No repeat offenders identified in current session.")

    # Timeline Update
    tl_data = timeline.get_timeline(limit=15)
    tl_html = ""
    for e in reversed(tl_data):
        item_class = "alert-warning" if e['details'] and e['details'].get('level') == 'MEDIUM' else "alert-critical" if e['details'] and e['details'].get('level') == 'HIGH' else ""
        tl_html += f"""
            <div class='timeline-item'>
                <div class='timeline-timestamp'>{e['timestamp']}</div>
                <div class='timeline-event'>{e['event'].upper()}</div>
            </div>
        """
    timeline_placeholder.markdown(tl_html, unsafe_allow_html=True)

# --- EXECUTION ---
if run_detection:
    if input_option == "Live Webcam":
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            # Use a frame counter for optimization
            if "frame_count" not in st.session_state:
                st.session_state.frame_count = 0
            st.session_state.frame_count += 1

            frame = cv2.resize(frame, (800, 600))
            processed_frame, alert_text, level = process_frame(frame)
            
            frame_placeholder.image(processed_frame, channels="BGR", use_container_width=True)
            
            # Alert Banner
            if level == "HIGH":
                alert_placeholder.markdown(f"<div class='alert-banner alert-critical'>ALERT: {alert_text}</div>", unsafe_allow_html=True)
                if enable_voice: st.toast(f"CRITICAL: {alert_text}")
            elif level == "MEDIUM":
                alert_placeholder.markdown(f"<div class='alert-banner alert-warning'>WARNING: {alert_text}</div>", unsafe_allow_html=True)
            else:
                alert_placeholder.markdown("<div class='alert-banner alert-safe'>SYSTEM SECURE - MONITORING ACTIVE</div>", unsafe_allow_html=True)

            # Optimization: Update metrics only every 30 frames
            if st.session_state.frame_count % 30 == 0:
                update_dashboard_metrics()
            
            if save_frame:
                save_path = f"outputs/capture_{int(time.time())}.jpg"
                cv2.imwrite(save_path, processed_frame)
                st.sidebar.success(f"Evidence captured")
                save_frame = False

            time.sleep(0.01)
        cap.release()

    elif input_option == "Upload Image" and uploaded_file:
        image = Image.open(uploaded_file)
        frame = np.array(image)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        processed_frame, alert_text, level = process_frame(frame)
        frame_placeholder.image(processed_frame, channels="BGR", use_container_width=True)
        update_dashboard_metrics()

    elif input_option == "Upload Video" and uploaded_video:
        with open("temp_video.mp4", "wb") as f: f.write(uploaded_video.read())
        cap = cv2.VideoCapture("temp_video.mp4")
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            frame = cv2.resize(frame, (800, 600))
            processed_frame, alert_text, level = process_frame(frame)
            frame_placeholder.image(processed_frame, channels="BGR", use_container_width=True)
            update_dashboard_metrics()
            time.sleep(0.01)
        cap.release()

# Clear Logs Logic
if clear_logs:
    db.data = {"incidents": [], "activity_counts": {}}
    db._save_data()
    cooldown_manager.reset()
    st.sidebar.success("All logs cleared successfully.")

# Report Generation
if generate_report:
    reporter = ReportGenerator()
    incidents = db.get_all_incidents()
    if incidents:
        report_path, html_content = reporter.generate_html_report(incidents)
        st.sidebar.success(f"Report Generated: {os.path.basename(report_path)}")
        st.sidebar.download_button(
            label="Download HTML Report",
            data=html_content,
            file_name=os.path.basename(report_path),
            mime="text/html",
            use_container_width=True,
            key=f"report_download_{int(time.time())}"
        )
    else:
        st.sidebar.warning("No incident data available.")

if not run_detection:
    st.markdown("""
        <div class='glass-card' style='text-align: center; padding: 100px;'>
            <h1 style='color: #00b4d8;'>AI-SURVEILLANCE SYSTEM</h1>
            <p style='color: #8d99ae;'>Initialize system from the control panel to start active monitoring.</p>
        </div>
    """, unsafe_allow_html=True)
