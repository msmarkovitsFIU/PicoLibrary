"""
main.py
Room Comfort Feedback Kiosk
Mini-Lab 3: State modeling using UML Statecharts
Author: ISM6106 Student
Target: Raspberry Pi Pico (MicroPython) / Wokwi Simulator
"""

import sys
if './PicoLibrary-main' not in sys.path:
    sys.path.append('./PicoLibrary-main')

import time
from FeedbackController import FeedbackController

def main():
    print("--------------------------------------------------")
    print("Starting Room Comfort Feedback Kiosk (Mini-Lab 3)")
    print("Hardware pinout:")
    print("  - LCD 1602 (I2C0): SDA=GP0, SCL=GP1")
    print("  - Ultrasonic Sensor: Trig=GP2, Echo=GP3")
    print("  - NeoPixel Ring (16 LEDs): DIN=GP6")
    print("  - Passive Buzzer: PWM=GP7")
    print("  - Just Right / Reset Button: GP10")
    print("  - Too Cold Button: GP11")
    print("  - Too Warm Button: GP12")
    print("  - Manager Mute Button: GP13")
    print("--------------------------------------------------")

    # Instantiate the controller with full configuration
    kiosk = FeedbackController(
        lcd_sda=0, lcd_scl=1,
        us_trig=2, us_echo=3,
        light_pin=6, pixel_count=16,
        buzzer_pin=7,
        btn_just_right_pin=10,
        btn_too_cold_pin=11,
        btn_too_warm_pin=12,
        btn_mute_pin=13,
        proximity_distance_cm=10.0,
        debug=True
    )

    print("Kiosk initialized in Welcome state. Running main loop...")

    try:
        while True:
            kiosk.update()
            time.sleep_ms(20)  # 50 Hz polling rate for responsive interaction
    except KeyboardInterrupt:
        print("\nStopping Kiosk...")
        kiosk._buzzer.stop()
        kiosk._lights.turn_off()
        kiosk._lcd.show_message("Kiosk Offline", "")
        print("Shutdown complete.")

if __name__ == '__main__':
    main()
