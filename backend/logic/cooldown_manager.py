import time

class CooldownManager:
    def __init__(self, default_cooldown=10):
        # last_log: dictionary to store {alert_type: last_timestamp}
        self.last_log = {}
        self.default_cooldown = default_cooldown

    def should_log(self, alert_type, cooldown=None):
        current_time = time.time()
        cd = cooldown if cooldown is not None else self.default_cooldown
        
        if alert_type not in self.last_log:
            self.last_log[alert_type] = current_time
            return True
        
        if current_time - self.last_log[alert_type] > cd:
            self.last_log[alert_type] = current_time
            return True
        
        return False

    def reset(self):
        self.last_log = {}
