# Anomaly detection logic
from dotenv import load_dotenv
import os

load_dotenv()

LATENCY_THRESHOLD_MS = float(os.getenv("LATENCY_THRESHOLD_MS", 1000))
ERROR_RATE_THRESHOLD = float(os.getenv("ERROR_RATE_THRESHOLD", 0.05))

class AnomalyDetector:
    def __init__(self):
        self.recent_logs = []        # stores last 100 logs
        self.error_count = 0         # tracks errors in recent window
        self.total_count = 0         # tracks total logs in recent window
        self.window_size = 100       # how many logs to analyse at once

    def add_log(self, level: str, latency_ms: float = None):
        """Add a new log and check for anomalies"""
        self.total_count += 1

        if level == "ERROR":
            self.error_count += 1

        # Keep only last 100 logs in memory
        self.recent_logs.append({"level": level, "latency_ms": latency_ms})
        if len(self.recent_logs) > self.window_size:
            oldest = self.recent_logs.pop(0)
            if oldest["level"] == "ERROR":
                self.error_count -= 1
            self.total_count -= 1

    def check_latency(self, latency_ms: float):
        """Check if response time is too high"""
        if latency_ms and latency_ms > LATENCY_THRESHOLD_MS:
            return {
                "is_anomaly": True,
                "anomaly_type": "HIGH_LATENCY",
                "detail": f"Latency {latency_ms}ms exceeds threshold of {LATENCY_THRESHOLD_MS}ms"
            }
        return {"is_anomaly": False}

    def check_error_rate(self):
        """Check if error rate is too high"""
        if self.total_count == 0:
            return {"is_anomaly": False}
        
        error_rate = self.error_count / self.total_count
        if error_rate > ERROR_RATE_THRESHOLD:
            return {
                "is_anomaly": True,
                "anomaly_type": "HIGH_ERROR_RATE",
                "detail": f"Error rate {error_rate:.2%} exceeds threshold of {ERROR_RATE_THRESHOLD:.2%}"
            }
        return {"is_anomaly": False}

    def analyse(self, level: str, latency_ms: float = None):
        """Run all checks and return any anomalies found"""
        self.add_log(level, latency_ms)
        
        anomalies = []
        
        latency_check = self.check_latency(latency_ms)
        if latency_check["is_anomaly"]:
            anomalies.append(latency_check)

        error_check = self.check_error_rate()
        if error_check["is_anomaly"]:
            anomalies.append(error_check)

        return anomalies

# Global detector instance
detector = AnomalyDetector()
