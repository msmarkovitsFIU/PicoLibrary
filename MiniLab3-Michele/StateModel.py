"""
StateModel.py
Finite State Machine model implementing UML Statechart transitions,
guards, actions, state entry, and state exit handlers.
Design Reference: Mini-Lab 3 Comfort Feedback Class Diagram & Feedback State Machine
"""

class StateModel:
    """
    Finite State Machine manager for the kiosk.
    Operations:
        +addTransition()
        +addButton()
        +addSensor()
        +processEvent()
    """
    def __init__(self, num_states: int = 6, handler=None, debug: bool = False):
        self._num_states = num_states
        self._handler = handler
        self._debug = debug
        self._current_state = 0
        self._transitions = []
        self._state_entries = {}
        self._state_exits = {}
        self._buttons = []
        self._sensors = []

    def set_state_entry(self, state: int, action) -> None:
        """Register the entry action callable for a state."""
        self._state_entries[state] = action

    def set_state_exit(self, state: int, action) -> None:
        """Register the exit action callable for a state."""
        self._state_exits[state] = action

    def addTransition(self, from_state: int, events, to_state: int, guard=None, action=None) -> None:
        """
        Add a transition rule from from_state to to_state on event(s).
        Optional guard condition function must evaluate to True for transition to fire.
        Optional action callable executes upon transition.
        """
        if isinstance(events, str):
            events = [events]
        for event in events:
            self._transitions.append({
                'from_state': from_state,
                'event': event,
                'to_state': to_state,
                'guard': guard,
                'action': action
            })

    def addButton(self, button) -> None:
        """Register a button with the state model."""
        self._buttons.append(button)

    def addSensor(self, sensor) -> None:
        """Register a sensor with the state model."""
        self._sensors.append(sensor)

    def get_current_state(self) -> int:
        """Return the current active state integer ID."""
        return self._current_state

    def start(self) -> None:
        """Start the state model at state 0 and run state 0 entry action."""
        self._current_state = 0
        if 0 in self._state_entries and self._state_entries[0]:
            self._state_entries[0]()

    def processEvent(self, event: str) -> bool:
        """
        Process an incoming event against the active state's transitions.
        Evaluates guard conditions. If satisfied, executes transition action,
        invokes the exit action of the source state, switches state, and
        invokes the entry action of the target state.
        For internal transitions (from_state == to_state), executes the action
        without invoking exit/entry actions.
        """
        if self._debug:
            print(f"[StateModel] State {self._current_state} received event: {event}")

        for trans in self._transitions:
            if trans['from_state'] == self._current_state and trans['event'] == event:
                guard = trans['guard']
                if guard is not None:
                    if not guard():
                        continue  # Guard condition not met, check next candidate

                # Guard passed: execute transition action
                action = trans['action']
                if action is not None:
                    action()

                to_state = trans['to_state']
                if to_state != self._current_state:
                    # Execute source state exit action
                    if self._current_state in self._state_exits and self._state_exits[self._current_state]:
                        self._state_exits[self._current_state]()

                    prev_state = self._current_state
                    self._current_state = to_state

                    if self._debug:
                        print(f"[StateModel] Transitioned from {prev_state} to {to_state} on event '{event}'")

                    # Execute target state entry action
                    if self._current_state in self._state_entries and self._state_entries[self._current_state]:
                        self._state_entries[self._current_state]()
                else:
                    if self._debug:
                        print(f"[StateModel] Handled internal event '{event}' in state {self._current_state}")

                return True

        return False
