class AlertEngine:
    def __init__(self):
        pass

    def get_center(self, box):
        x1, y1, x2, y2 = box
        return ((x1 + x2) // 2, (y1 + y2) // 2)

    def distance(self, p1, p2):
        return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

    def analyze(self, persons, weapons, criminal_detected, aggressive_posture):
        alert = "SAFE"
        level = "LOW"

        if len(weapons) > 0 and len(persons) > 0:
            alert = "HIGH ALERT 🚨"
            level = "HIGH"
        elif criminal_detected:
            alert = "CRIMINAL DETECTED"
            level = "HIGH"
        elif aggressive_posture:
            alert = "AGGRESSIVE POSTURE"
            level = "MEDIUM"
        elif len(persons) >= 2:
            c1 = self.get_center(persons[0])
            c2 = self.get_center(persons[1])
            if self.distance(c1, c2) < 150:
                alert = "SUSPICIOUS BEHAVIOR"
                level = "MEDIUM"
        elif len(weapons) > 0:
            alert = "WEAPON DETECTED"
            level = "MEDIUM"

        return alert, level
