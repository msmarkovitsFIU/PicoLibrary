"""
LightStrip.py
NeoPixel light strip / ring controller.
Design Reference: Mini-Lab 3 Comfort Feedback Class Diagram
"""

from machine import Pin
import neopixel

class LightStrip:
    """
    NeoPixel LED ring/strip controlling all pixels uniformly.
    Attributes:
        -data_pin : Pin
        -pixel_count : int
    """
    # RGB color mapping
    COLOR_MAP = {
        'green': (0, 128, 0),
        'yellow': (128, 100, 0),
        'blue': (0, 0, 128),
        'red': (128, 0, 0),
        'off': (0, 0, 0),
        'black': (0, 0, 0)
    }

    def __init__(self, data_pin=6, pixel_count: int = 16):
        if isinstance(data_pin, int):
            self._data_pin = Pin(data_pin, Pin.OUT)
        else:
            self._data_pin = data_pin
        self._pixel_count = pixel_count
        self._np = neopixel.NeoPixel(self._data_pin, self._pixel_count)
        self.turn_off()

    def set_color(self, color: str) -> None:
        """Set all pixels to the named color ('green', 'yellow', 'blue', 'red', 'off')."""
        c_str = color.lower()
        rgb = self.COLOR_MAP.get(c_str, (0, 0, 0))
        for i in range(self._pixel_count):
            self._np[i] = rgb
        self._np.write()

    def turn_off(self) -> None:
        """Turn off all pixels."""
        for i in range(self._pixel_count):
            self._np[i] = (0, 0, 0)
        self._np.write()
