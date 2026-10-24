"""
# MysteryGadget.py
# MysteryGadget engine simulator using an LCD display, buzzer, NeoPixel strip, and potentiometer
# Author: Michele Markovits
"""

import time
from Log import *

# Tachometer color definitions (RGB)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 200, 0)
RED = (255, 0, 0)


class MysteryGadget:
    """
    **MysteryGadget** simulates an automobile engine dashboard using an LCD display,
    a buzzer, a NeoPixel light strip, and a potentiometer throttle.

    The gadget simulates engine ignition with low-frequency rumble sounds,
    continuous throttle control translating potentiometer readings into engine RPM,
    speed, tachometer LED illumination, and pitch variation, and graceful shutdown.

    Parameters:
    ----------
    display : LCDDisplay or Display
        The LCD display instance used to show simulated RPM, speed, and status messages.
    buzzer : PassiveBuzzer or Buzzer
        The buzzer instance used to produce engine rumble and revving sounds.
    light_strip : LightStrip
        The NeoPixel light strip used to visualize engine RPM as a tachometer.
    potentiometer : AnalogSensor
        The potentiometer / analog sensor instance used as the throttle input.
    num_leds : int, optional
        Number of NeoPixel LEDs on the light strip (default: 16).
    min_rpm : int, optional
        Idle RPM of the engine (default: 800).
    max_rpm : int, optional
        Maximum / redline RPM of the engine (default: 7000).
    max_speed : int, optional
        Maximum simulated vehicle speed in mph (default: 120).

    Examples:
    ---------
    1. Basic setup and control:
        ```python
        from Displays import LCDDisplay
        from Buzzer import PassiveBuzzer
        from LightStrip import LightStrip
        from Sensors import AnalogSensor
        from MysteryGadget import MysteryGadget

        lcd = LCDDisplay(sda=0, scl=1)
        buzzer = PassiveBuzzer(pin=15)
        strip = LightStrip(pin=2, numleds=16)
        pot = AnalogSensor(pin=26)

        gadget = MysteryGadget(lcd, buzzer, strip, pot)
        gadget.start()
        gadget.control(duration=10)
        gadget.stop()
        ```
    """

    def __init__(self, display, buzzer, light_strip, potentiometer,
                 num_leds=16, min_rpm=800, max_rpm=7000, max_speed=120):
        """
        Initialize the MysteryGadget with display, buzzer, light strip, and potentiometer.

        Parameters:
        ----------
        display : LCDDisplay or Display
            LCD display instance.
        buzzer : PassiveBuzzer or Buzzer
            Buzzer instance.
        light_strip : LightStrip
            NeoPixel light strip instance.
        potentiometer : AnalogSensor
            Potentiometer / analog sensor instance.
        num_leds : int, optional
            Number of LEDs on the strip (default: 16).
        min_rpm : int, optional
            Idle RPM (default: 800).
        max_rpm : int, optional
            Max RPM (default: 7000).
        max_speed : int, optional
            Max speed in mph (default: 120).

        Examples:
        ---------
        1. Initialize gadget:
            ```python
            gadget = MysteryGadget(lcd, buzzer, strip, pot)
            ```
        """
        self.display = display
        self.buzzer = buzzer
        self.light_strip = light_strip
        self.potentiometer = potentiometer

        self.num_leds = getattr(light_strip, '_numleds', num_leds) if light_strip else num_leds
        self.min_rpm = min_rpm
        self.max_rpm = max_rpm
        self.max_speed = max_speed
        self._running = False

        Log.i("MysteryGadget: Initialized")

    def start(self):
        """
        Simulate starting of the engine.

        Produces a sequence of low-frequency engine cranking tones on the buzzer,
        initializes the tachometer light strip to idle, and displays initial
        idle RPM and speed values on the LCD display.

        Parameters:
        ----------
        None

        Examples:
        ---------
        1. Start the engine simulator:
            ```python
            gadget.start()
            ```
        """
        Log.i("MysteryGadget: Starting engine...")
        self._running = True

        # Initial starting message on display
        if self.display:
            self.display.clear()
            self.display.showText("Starting Engine", row=0, col=0)
            self.display.showText("Please wait...", row=1, col=0)

        # Simulate engine starter cranking with low-frequency tones
        crank_tones = [55, 75, 60, 95, 80, 70]
        for tone in crank_tones:
            if self.buzzer:
                self.buzzer.play(tone)
            time.sleep(0.12)

        # Settle on a low-frequency idle rumble tone
        if self.buzzer:
            self.buzzer.play(65)

        # Initialize light strip with idle indicator (1 green LED)
        if self.light_strip:
            self.light_strip.off()
            self.light_strip.setPixel(0, GREEN, show=True)

        # Display initial simulated idle RPM and speed
        if self.display:
            self.display.clear()
            line0 = f"RPM: {self.min_rpm}"
            line1 = "Speed: 0%"
            self.display.showText(f"{line0:<16}"[:16], row=0, col=0)
            self.display.showText(f"{line1:<16}"[:16], row=1, col=0)

        Log.i(f"MysteryGadget: Engine started at {self.min_rpm} RPM")

    def stop(self):
        """
        Stop the engine simulation.

        Stops buzzer sounds, turns off all LEDs on the light strip,
        and displays "Engine Stopped" on the LCD display.

        Parameters:
        ----------
        None

        Examples:
        ---------
        1. Stop the engine simulator:
            ```python
            gadget.stop()
            ```
        """
        Log.i("MysteryGadget: Stopping engine...")
        self._running = False

        # Stop buzzer sound
        if self.buzzer:
            self.buzzer.stop()

        # Turn off light strip
        if self.light_strip:
            self.light_strip.off()

        # Update display
        if self.display:
            self.display.clear()
            self.display.showText("Engine Stopped", row=0, col=0)

        Log.i("MysteryGadget: Engine stopped")

    def control(self, duration=None, steps=None, delay=0.05):
        """
        Monitor the potentiometer and simulate dynamic engine control.

        Continuously reads the potentiometer throttle, dynamically scales RPM and speed,
        adjusts buzzer pitch to reflect engine load, lights up the NeoPixel tachometer
        with green/yellow/red color staging, and displays live RPM and speed on the LCD.

        Parameters:
        ----------
        duration : float, optional
            Total monitoring duration in seconds. If None, runs indefinitely until
            stopped or interrupted (default: None).
        steps : int, optional
            Maximum number of monitoring sample iterations to execute (default: None).
        delay : float, optional
            Delay between reading samples in seconds (default: 0.05).

        Examples:
        ---------
        1. Run live monitoring loop indefinitely:
            ```python
            gadget.control()
            ```
        2. Run monitoring loop for 10 seconds:
            ```python
            gadget.control(duration=10.0)
            ```
        3. Run for 50 sample steps:
            ```python
            gadget.control(steps=50)
            ```
        """
        if not self._running:
            Log.i("MysteryGadget: Engine not running; starting engine first...")
            self.start()

        Log.i("MysteryGadget: Monitoring throttle potentiometer...")
        start_time = time.time()
        step_count = 0

        try:
            while self._running:
                if duration is not None and (time.time() - start_time) >= duration:
                    break
                if steps is not None and step_count >= steps:
                    break

                # 1. Read raw throttle value from potentiometer (0 - 65535)
                raw_val = self._read_potentiometer()
                if raw_val < 0:
                    raw_val = 0
                elif raw_val > 65535:
                    raw_val = 65535

                ratio = raw_val / 65535.0

                # 2. Compute simulated RPM, Speed, and Engine Audio Pitch
                rpm = int(self.min_rpm + ratio * (self.max_rpm - self.min_rpm))
                speed = int(ratio * self.max_speed)
                pitch = int(500 + ratio * (1500 - 500))  # Low idle hum up to high rev tone

                # 3. Update buzzer pitch
                if self.buzzer:
                    self.buzzer.play(pitch)

                # 4. Update NeoPixel light strip tachometer
                if self.light_strip:
                    active_leds = int(ratio * self.num_leds)
                    if ratio > 0.02 and active_leds == 0:
                        active_leds = 1

                    for i in range(self.num_leds):
                        if i < active_leds:
                            pos_ratio = i / float(self.num_leds)
                            if pos_ratio < 0.6:
                                color = GREEN
                            elif pos_ratio < 0.85:
                                color = YELLOW
                            else:
                                color = RED
                            self.light_strip.setPixel(i, color, show=False)
                        else:
                            self.light_strip.setPixel(i, BLACK, show=False)
                    self.light_strip.show()

                # 5. Update LCD Display with RPM and Speed
                if self.display:
                    line0 = f"RPM: {rpm}"
                    line1 = f"Speed: {int(ratio * 100)}%"
                    self.display.showText(f"{line0:<16}"[:16], row=0, col=0)
                    self.display.showText(f"{line1:<16}"[:16], row=1, col=0)

                step_count += 1
                time.sleep(delay)

        except KeyboardInterrupt:
            Log.i("MysteryGadget: Monitoring interrupted by user")
            self.stop()

    def _read_potentiometer(self):
        """Internal helper to read raw ADC value across various sensor interfaces."""
        if hasattr(self.potentiometer, 'rawValue'):
            return self.potentiometer.rawValue()
        elif hasattr(self.potentiometer, 'read_u16'):
            return self.potentiometer.read_u16()
        elif callable(self.potentiometer):
            return self.potentiometer()
        elif isinstance(self.potentiometer, (int, float)):
            return int(self.potentiometer)
        return 0


# Test execution block for verification
if __name__ == "__main__":
    Log.i("Testing MysteryGadget: Initializing mock peripherals...")

    # Mock implementations for self-contained desktop and unit test verification
    class MockLCDDisplay:
        def __init__(self):
            self.rows = ["", ""]
            self.cleared = False

        def clear(self, line=-1):
            self.cleared = True
            self.rows = ["", ""]

        def showText(self, text, row=0, col=0):
            self.rows[row] = text
            Log.i(f"MockLCD [row {row}]: {text.strip()}")

    class MockPassiveBuzzer:
        def __init__(self):
            self.current_tone = None
            self.is_playing = False

        def play(self, tone):
            self.current_tone = tone
            self.is_playing = True
            Log.i(f"MockBuzzer: Playing tone {tone} Hz")

        def stop(self):
            self.is_playing = False
            self.current_tone = None
            Log.i("MockBuzzer: Tone stopped")

    class MockLightStrip:
        def __init__(self, numleds=16):
            self._numleds = numleds
            self.pixels = [BLACK] * numleds

        def setPixel(self, pixelno, color, show=True):
            if 0 <= pixelno < self._numleds:
                self.pixels[pixelno] = color

        def show(self):
            lit = sum(1 for p in self.pixels if p != BLACK)
            Log.i(f"MockLightStrip: Tachometer updated ({lit}/{self._numleds} LEDs lit)")

        def off(self):
            self.pixels = [BLACK] * self._numleds
            Log.i("MockLightStrip: All LEDs turned off")

    class MockPotentiometer:
        def __init__(self, value=0):
            self.value = value

        def rawValue(self):
            return self.value

    # Instantiate mock components
    mock_display = MockLCDDisplay()
    mock_buzzer = MockPassiveBuzzer()
    mock_strip = MockLightStrip(numleds=16)
    mock_pot = MockPotentiometer(value=0)

    # 1. Instantiate MysteryGadget
    gadget = MysteryGadget(
        display=mock_display,
        buzzer=mock_buzzer,
        light_strip=mock_strip,
        potentiometer=mock_pot,
        num_leds=16,
        min_rpm=800,
        max_rpm=7000,
        max_speed=120
    )

    # 2. Test start()
    Log.i("--- Testing start() ---")
    gadget.start()
    assert gadget._running is True, "Engine should be running after start()"
    assert mock_buzzer.is_playing is True, "Buzzer should be playing low-frequency idle tone"
    assert "RPM: 800" in mock_display.rows[0], "Display row 0 should show idle RPM"
    assert "Speed: 0%" in mock_display.rows[1], "Display row 1 should show 0%"

    # 3. Test control() at Idle throttle
    Log.i("--- Testing control() at Idle (0) ---")
    mock_pot.value = 0
    gadget.control(steps=1, delay=0.01)
    assert "RPM: 800" in mock_display.rows[0], "Display should show min RPM"

    # 4. Test control() at Mid-throttle (~50%)
    Log.i("--- Testing control() at Mid-throttle (32768) ---")
    mock_pot.value = 32768
    gadget.control(steps=1, delay=0.01)
    assert mock_buzzer.current_tone > 100, "Buzzer frequency should increase with throttle"

    # 5. Test control() at Full throttle (65535)
    Log.i("--- Testing control() at Full throttle (65535) ---")
    mock_pot.value = 65535
    gadget.control(steps=1, delay=0.01)
    assert "RPM: 7000" in mock_display.rows[0], "Display should show max RPM"
    assert "Speed: 100%" in mock_display.rows[1], "Display should show max speed"

    # 6. Test stop()
    Log.i("--- Testing stop() ---")
    gadget.stop()
    assert gadget._running is False, "Engine should not be running after stop()"
    assert mock_buzzer.is_playing is False, "Buzzer should be stopped"
    assert "Engine Stopped" in mock_display.rows[0], "Display should show 'Engine Stopped'"

    Log.i("Testing complete - all checks passed")
