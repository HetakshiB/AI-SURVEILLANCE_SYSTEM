from datetime import datetime
import collections

class BehaviorAnalysis:
    def __init__(self, db):
        self.db = db

    def get_peak_hours(self):
        incidents = self.db.get_all_incidents()
        hours = [datetime.fromisoformat(i['timestamp']).hour for i in incidents]
        if not hours:
            return {}
        counts = collections.Counter(hours)
        return dict(counts)

    def get_repeat_offenders(self):
        incidents = self.db.get_all_incidents()
        offenders = []
        for i in incidents:
            if i['alert'] == 'CRIMINAL DETECTED' and 'name' in i.get('details', {}):
                offenders.append(i['details']['name'])
        
        counts = collections.Counter(offenders)
        return {name: count for name, count in counts.items() if count > 1}

    def get_activity_trends(self):
        # Could expand this to daily/weekly trends
        return self.db.get_analytics()["activity_counts"]
