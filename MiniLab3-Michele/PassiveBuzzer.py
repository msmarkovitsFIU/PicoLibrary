"""
PassiveBuzzer.py
PWM-driven passive buzzer for alarm notifications.
Design Reference: Mini-Lab 3 Comfort Feedback Class Diagram
"""

from machine import Pin, PWM

class PassiveBuzzer:
    """
    Passive buzzer controlled via PWM frequency and duty cycle.
    Attributes:
        -pwm : PWM
    """
    def __init__(self, pin=7):
        if isinstance(pin, int):
            self._pwm = PWM(Pin(pin))
        else:
            self._pwm = PWM(pin)
        self.stop()

    def start_alarm(self) -> None:
        """Start playing the alarm tone at 1000 Hz with 50% duty cycle."""
        self._pwm.freq(1000)
        self._pwm.duty_u16(32768)

    def stop(self) -> None:
        """Stop tone output by setting duty cycle to 0."""
        self._pwm.duty_u16(0)
