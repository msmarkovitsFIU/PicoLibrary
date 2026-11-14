"""
Button.py
Polled push-button with edge detection and debouncing.
Design Reference: Mini-Lab 3 Comfort Feedback Class Diagram
"""

from machine import Pin
import time

class Button:
    """
    Button component with edge detection so each physical press
    is detected exactly once, even if the button remains held down.
    Attributes:
        -pin : Pin
        -event_name : str
    """
    def __init__(self, pin, event_name: str = 'button_press'):
        if isinstance(pin, int):
            self._pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        else:
            self._pin = pin
        self._event_name = event_name
        self._last_state = 1  # Active-low with pull-up: 1 = unpressed, 0 = pressed
        self._last_press_time = 0
        self._debounce_ms = 50

    def was_pressed(self) -> bool:
        """
        Poll button state. Returns True once per press (falling edge: 1 -> 0).
        Returns False while button is held down.
        """
        current_state = self._pin.value()
        now = time.ticks_ms()
        pressed = False

        if self._last_state == 1 and current_state == 0:
            if time.ticks_diff(now, self._last_press_time) > self._debounce_ms:
                pressed = True
                self._last_press_time = now

        self._last_state = current_state
        return pressed
