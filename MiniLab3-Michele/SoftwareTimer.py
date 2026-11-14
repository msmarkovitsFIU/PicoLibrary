"""
SoftwareTimer.py
Non-blocking software timer using MicroPython time ticks.
Design Reference: Mini-Lab 3 Comfort Feedback Class Diagram
"""

import time

class SoftwareTimer:
    """
    Software timer supporting millisecond deadlines.
    Attributes:
        -deadline_ms : int
        -active : bool = false
    """
    def __init__(self):
        self._deadline_ms = 0
        self._active = False

    def start(self, duration_ms: int) -> None:
        """Start the timer for a specific duration in milliseconds."""
        self._deadline_ms = time.ticks_add(time.ticks_ms(), int(duration_ms))
        self._active = True

    def stop(self) -> None:
        """Cancel/deactivate the timer so it cannot expire."""
        self._active = False

    def has_expired(self) -> bool:
        """
        Check if deadline has passed.
        If expired, automatically deactivates and returns True once.
        Returns False on subsequent calls until restarted.
        """
        if not self._active:
            return False
        if time.ticks_diff(time.ticks_ms(), self._deadline_ms) >= 0:
            self._active = False  # Ensure single-shot firing per cycle
            return True
        return False
