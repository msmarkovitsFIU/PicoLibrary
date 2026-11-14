"""
FeedbackController.py
Coordinates hardware subsystems and manages application states according to
the UML Class Diagram and Feedback State Machine.
Design Reference: Mini-Lab 3 Comfort Feedback Class Diagram & Feedback State Machine
"""

from FeedbackStats import FeedbackStats
from SoftwareTimer import SoftwareTimer
from StateModel import StateModel
from PassiveBuzzer import PassiveBuzzer
from LightStrip import LightStrip
from LCDDisplay import LCDDisplay
from UltrasonicSensor import UltrasonicSensor
from Button import Button

class FeedbackController:
    """
    Central controller orchestrating feedback kiosk interactions.
    Attributes:
        -voting_timeout_ms : int = 10000
        -acknowledgment_timeout_ms : int = 5000
        -alarm_threshold_pct : float = 30.0
    Operations:
        +update() : void
        +show_welcome() : void
        +show_voting_prompt() : void
        +show_vote_acknowledgment() : void
        +start_alarm() : void
        +mute_alarm() : void
        +reset_feedback() : void
    """
    def __init__(self,
                 lcd_sda: int = 0, lcd_scl: int = 1,
                 us_trig: int = 2, us_echo: int = 3,
                 light_pin: int = 6, pixel_count: int = 16,
                 buzzer_pin: int = 7,
                 btn_just_right_pin: int = 10,
                 btn_too_cold_pin: int = 11,
                 btn_too_warm_pin: int = 12,
                 btn_mute_pin: int = 13,
                 proximity_distance_cm: float = 10.0,
                 debug: bool = False):

        # UML-specified attributes
        self._voting_timeout_ms = 10000
        self._acknowledgment_timeout_ms = 5000
        self._alarm_threshold_pct = 30.0

        # Operational parameters & tracking
        self._proximity_distance_cm = proximity_distance_cm
        self._sensor_armed = True
        self._last_vote = None

        # Instantiate Model & Hardware components
        self._stats = FeedbackStats()
        self._timer = SoftwareTimer()
        self._lcd = LCDDisplay(sda=lcd_sda, scl=lcd_scl)
        self._lights = LightStrip(data_pin=light_pin, pixel_count=pixel_count)
        self._buzzer = PassiveBuzzer(pin=buzzer_pin)
        self._sensor = UltrasonicSensor(trigger_pin=us_trig, echo_pin=us_echo)

        # 4 physical buttons: 3 voting buttons + 1 manager mute button
        self._btn_just_right = Button(pin=btn_just_right_pin, event_name='just_right_press')
        self._btn_too_cold = Button(pin=btn_too_cold_pin, event_name='too_cold_press')
        self._btn_too_warm = Button(pin=btn_too_warm_pin, event_name='too_warm_press')
        self._btn_mute = Button(pin=btn_mute_pin, event_name='manager_mute_press')
        self._buttons = [
            self._btn_just_right,
            self._btn_too_cold,
            self._btn_too_warm,
            self._btn_mute
        ]

        # Initialize StateModel with 6 states (0 through 5)
        self._state_model = StateModel(num_states=6, handler=self, debug=debug)
        for btn in self._buttons:
            self._state_model.addButton(btn)
        self._state_model.addSensor(self._sensor)

        # Configure state entry actions
        self._state_model.set_state_entry(0, self.show_welcome)
        self._state_model.set_state_entry(1, self.show_voting_prompt)
        self._state_model.set_state_entry(2, self.show_vote_acknowledgment)
        self._state_model.set_state_entry(3, self.show_vote_acknowledgment)
        self._state_model.set_state_entry(4, self.show_vote_acknowledgment)
        self._state_model.set_state_entry(5, self.start_alarm)

        # Configure state exit actions (Stop timer when leaving Selection)
        self._state_model.set_state_exit(1, self._timer.stop)

        # State 0: Welcome transitions
        self._state_model.addTransition(0, 'uss_trip', 1)

        # State 1: Selection transitions
        self._state_model.addTransition(1, 'timer_timeout', 0)
        self._state_model.addTransition(1, 'just_right_press', 2,
                                        action=self._handle_just_right_vote)
        self._state_model.addTransition(1, 'too_cold_press', 3,
                                        action=self._handle_too_cold_vote)
        self._state_model.addTransition(1, 'too_warm_press', 4,
                                        action=self._handle_too_warm_vote)

        # State 2: Just Right transitions (always returns to Welcome)
        self._state_model.addTransition(2, 'timer_timeout', 0)

        # State 3: Too Cold transitions (guarded by comfort percentage)
        self._state_model.addTransition(
            3, 'timer_timeout', 0,
            guard=lambda: self._stats.get_comfort_percentage() >= self._alarm_threshold_pct
        )
        self._state_model.addTransition(
            3, 'timer_timeout', 5,
            guard=lambda: self._stats.get_comfort_percentage() < self._alarm_threshold_pct
        )

        # State 4: Too Warm transitions (guarded by comfort percentage)
        self._state_model.addTransition(
            4, 'timer_timeout', 0,
            guard=lambda: self._stats.get_comfort_percentage() >= self._alarm_threshold_pct
        )
        self._state_model.addTransition(
            4, 'timer_timeout', 5,
            guard=lambda: self._stats.get_comfort_percentage() < self._alarm_threshold_pct
        )

        # State 5: Alarm transitions & internal events
        self._state_model.addTransition(5, 'reset_press', 0, action=self.reset_feedback)
        self._state_model.addTransition(5, 'manager_mute_press', 5, action=self.mute_alarm)

        # Start state machine in State 0
        self._state_model.start()

    # --- Transition vote recording helpers ---
    def _handle_just_right_vote(self) -> None:
        self._stats.add_just_right()
        self._last_vote = 'just_right'

    def _handle_too_cold_vote(self) -> None:
        self._stats.add_too_cold()
        self._last_vote = 'too_cold'

    def _handle_too_warm_vote(self) -> None:
        self._stats.add_too_warm()
        self._last_vote = 'too_warm'

    # --- UML Operations ---
    def show_welcome(self) -> None:
        """
        State 0 entry: Welcome screen.
        Displays 'Welcome!' on line 1.
        Line 2 shows overall trend or remains blank if zero votes.
        LED ring shows overall leader (Green=JR, Blue=TC, Yellow=TW, Off=tie/none).
        """
        self._buzzer.stop()
        self._timer.stop()
        total = self._stats.get_total_count()
        trend = self._stats.get_trend()

        if total == 0:
            self._lcd.show_message("Welcome!", "")
            self._lights.turn_off()
        else:
            self._lcd.show_message("Welcome!", trend)
            if trend == "Just Right leads":
                self._lights.set_color('green')
            elif trend == "Trend: Too Cold":
                self._lights.set_color('blue')
            elif trend == "Trend: Too Warm":
                self._lights.set_color('yellow')
            else:  # "Trend: Mixed" (tie)
                self._lights.turn_off()

    def show_voting_prompt(self) -> None:
        """
        State 1 entry: Prompt user to vote.
        Displays 'How's the temp?' and 'Press a button'.
        Starts 10-second voting timer.
        Retains overall trend LED color from Welcome.
        """
        self._lcd.show_message("How's the temp?", "Press a button")
        self._timer.start(self._voting_timeout_ms)

    def show_vote_acknowledgment(self) -> None:
        """
        State 2, 3, 4 entry: Acknowledge vote.
        Displays 'Thank you!' on line 1 and 'Have a great day' on line 2.
        Shows color of individual vote just cast (JR=Green, TC=Blue, TW=Yellow).
        Voting and acknowledgment remain silent.
        Starts 5-second acknowledgment timer.
        Preserves UML signature: inspects active state/last vote to determine color.
        """
        self._buzzer.stop()
        cur_state = self._state_model.get_current_state()

        if cur_state == 2 or self._last_vote == 'just_right':
            color = 'green'
        elif cur_state == 3 or self._last_vote == 'too_cold':
            color = 'blue'
        elif cur_state == 4 or self._last_vote == 'too_warm':
            color = 'yellow'
        else:
            color = 'off'

        self._lcd.show_message("Thank you!", "Have a great day")
        self._lights.set_color(color)
        self._timer.start(self._acknowledgment_timeout_ms)

    def start_alarm(self) -> None:
        """
        State 5 entry: Comfort Alert.
        Displays 'Comfort Alert' on LCD, turns LED ring red,
        and starts passive buzzer alert for manager's office.
        """
        self._lcd.show_message("Comfort Alert", "")
        self._lights.set_color('red')
        self._buzzer.start_alarm()

    def mute_alarm(self) -> None:
        """
        Internal event in State 5: Manager Mute.
        Silences the buzzer while remaining in Alarm with red ring.
        """
        self._buzzer.stop()

    def reset_feedback(self) -> None:
        """
        Transition action from State 5 to 0 on reset_press.
        Clears vote tallies, stops buzzer, and turns off LED ring.
        """
        self._stats.reset()
        self._buzzer.stop()
        self._lights.turn_off()
        self._last_vote = None

    def update(self) -> None:
        """
        Periodic polling cycle:
        1. Ultrasonic proximity detection with sensor re-arming.
        2. SoftwareTimer expiration processing.
        3. Button press edge detection and event dispatching.
        """
        # 1. Ultrasonic Sensor check
        dist = self._sensor.read_distance_cm()
        if dist > 0:
            if dist <= self._proximity_distance_cm:
                if self._sensor_armed and self._state_model.get_current_state() == 0:
                    self._sensor_armed = False
                    self._state_model.processEvent('uss_trip')
            else:
                # Visitor moved out of sensor range (> 10cm): re-arm for next approach
                if not self._sensor_armed:
                    self._sensor_armed = True

        # 2. Timer expiration check
        if self._timer.has_expired():
            self._state_model.processEvent('timer_timeout')

        # 3. Physical button edge detection
        for btn in self._buttons:
            if btn.was_pressed():
                event = btn._event_name
                # In Alarm (State 5), Just Right button sends reset_press
                if self._state_model.get_current_state() == 5 and btn == self._btn_just_right:
                    event = 'reset_press'
                self._state_model.processEvent(event)
