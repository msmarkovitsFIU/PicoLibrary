"""
UltrasonicSensor.py
HC-SR04 ultrasonic distance sensor.
Design Reference: Mini-Lab 3 Comfort Feedback Class Diagram
"""

from machine import Pin, time_pulse_us
import time

class UltrasonicSensor:
    """
    Ultrasonic distance measurement sensor.
    Attributes:
        -trigger_pin : Pin
        -echo_pin : Pin
    """
    def __init__(self, trigger_pin=2, echo_pin=3):
        if isinstance(trigger_pin, int):
            self._trigger_pin = Pin(trigger_pin, Pin.OUT)
        else:
            self._trigger_pin = trigger_pin

        if isinstance(echo_pin, int):
            self._echo_pin = Pin(echo_pin, Pin.IN)
        else:
            self._echo_pin = echo_pin

        self._trigger_pin.low()

    def read_distance_cm(self) -> float:
        """
        Send a 10us trigger pulse and measure the echo return pulse.
        Calculates and returns distance in centimeters, or -1.0 on timeout.
        """
        self._trigger_pin.low()
        time.sleep_us(2)
        self._trigger_pin.high()
        time.sleep_us(10)
        self._trigger_pin.low()

        pulse_duration = time_pulse_us(self._echo_pin, 1, 30000)
        if pulse_duration < 0:
            return -1.0

        distance_cm = (pulse_duration * 0.0343) / 2.0
        return round(distance_cm, 2)
