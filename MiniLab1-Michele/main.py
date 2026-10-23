"""
# main.py
# Main script to run MysteryGadget engine simulator on Raspberry Pi Pico
# Author: insert your name here
"""

import time
from Log import *
from Displays import LCDDisplay
from Buzzer import PassiveBuzzer
from LightStrip import LightStrip
from Sensors import AnalogSensor
from MysteryGadget import MysteryGadget


def main():
    Log.i("main: Initializing hardware components for MysteryGadget...")

    # Hardware pin mapping:
    # - LCD Display: I2C0 on GP0 (SDA), GP1 (SCL)
    # - Passive Buzzer: GP16
    # - NeoPixel Light Strip: GP2 (8 LEDs)
    # - Potentiometer (Throttle): ADC0 / GP26
    lcd = LCDDisplay(sda=0, scl=1)
    buzzer = PassiveBuzzer(pin=16, name="EngineBuzzer")
    strip = LightStrip(pin=2, name="Tachometer", numleds=8, brightness=0.5)
    pot = AnalogSensor(pin=26, name="ThrottlePot", lowActive=False)

    # Instantiate the MysteryGadget
    gadget = MysteryGadget(
        display=lcd,
        buzzer=buzzer,
        light_strip=strip,
        potentiometer=pot,
        num_leds=8,
        min_rpm=800,
        max_rpm=7000,
        max_speed=120
    )

    try:
        # 1. Start the mystery gadget engine
        Log.i("main: Starting MysteryGadget...")
        gadget.start()

        # 2. Monitor the mystery gadget continuously
        Log.i("main: Controlling MysteryGadget continuously...")
        gadget.control(delay=0.05)

    except KeyboardInterrupt:
        Log.w("main: Interrupted by user")

    finally:
        # 3. Stop the mystery gadget
        Log.i("main: Stopping MysteryGadget...")
        gadget.stop()
        Log.i("main: Execution complete")


if __name__ == "__main__":
    main()
