from datetime import datetime, timedelta
from enum import Enum

class TimelineSpeed(str, Enum):
    PAUSED = "PAUSED"
    NORMAL = "1x"
    FAST = "5x"
    ULTRA = "10x"

class Clock:
    """Orologio simulativo (giorni/ore)"""
    def __init__(self, start_time: datetime):
        self.current_time = start_time
        self.speed = TimelineSpeed.PAUSED

    def tick(self, interval_seconds: float):
        if self.speed == TimelineSpeed.PAUSED:
            return

        multiplier = 1.0
        if self.speed == TimelineSpeed.NORMAL: multiplier = 1.0
        elif self.speed == TimelineSpeed.FAST: multiplier = 5.0
        elif self.speed == TimelineSpeed.ULTRA: multiplier = 10.0

        self.current_time += timedelta(seconds=interval_seconds * multiplier)
