"""
LCDDisplay.py
I2C LCD 1602 Display interface.
Design Reference: Mini-Lab 3 Comfort Feedback Class Diagram
"""

from machine import Pin, I2C
try:
    from pico_i2c_lcd import I2cLcd
except ImportError:
    import sys
    if './PicoLibrary-main' not in sys.path:
        sys.path.append('./PicoLibrary-main')
    from pico_i2c_lcd import I2cLcd

class LCDDisplay:
    """
    LCD 1602 text display connected via I2C backpack.
    Attributes:
        -i2c : I2C
        -address : int
    """
    def __init__(self, sda=0, scl=1, i2c_id: int = 0, address=None):
        self._i2c = I2C(i2c_id, sda=Pin(sda), scl=Pin(scl), freq=400000)
        if address is None:
            devices = self._i2c.scan()
            self._address = devices[0] if devices else 0x27
        else:
            self._address = address
        self._lcd = I2cLcd(self._i2c, self._address, 2, 16)
        self._lcd.clear()

    def show_message(self, line1: str, line2: str = "") -> None:
        """
        Display two lines of text on the 16x2 LCD.
        Clears screen first and truncates lines to 16 characters.
        """
        self._lcd.clear()
        if line1:
            self._lcd.move_to(0, 0)
            self._lcd.putstr(line1[:16])
        if line2:
            self._lcd.move_to(0, 1)
            self._lcd.putstr(line2[:16])
