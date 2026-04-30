import pyttsx3
import threading

class VoiceEngine:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 1.0)
        self._lock = threading.Lock()

    def speak(self, text):
        def _speak():
            with self._lock:
                self.engine.say(text)
                self.engine.runAndWait()
        
        # Run in a separate thread to avoid blocking the UI
        threading.Thread(target=_speak, daemon=True).start()
