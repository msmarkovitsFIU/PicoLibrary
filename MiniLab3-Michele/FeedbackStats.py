"""
FeedbackStats.py
Maintains vote tallies and calculates comfort percentage and trend statistics.
Design Reference: Mini-Lab 3 Comfort Feedback Class Diagram
"""

class FeedbackStats:
    """
    Tracks votes for room comfort and computes metrics.
    Attributes:
        -just_right_count : int = 0
        -too_cold_count : int = 0
        -too_warm_count : int = 0
    """
    def __init__(self):
        self._just_right_count = 0
        self._too_cold_count = 0
        self._too_warm_count = 0

    def add_just_right(self) -> None:
        """Increment positive/comfortable votes."""
        self._just_right_count += 1

    def add_too_cold(self) -> None:
        """Increment too cold votes."""
        self._too_cold_count += 1

    def add_too_warm(self) -> None:
        """Increment too warm votes."""
        self._too_warm_count += 1

    def get_total_count(self) -> int:
        """Return total number of votes cast."""
        return self._just_right_count + self._too_cold_count + self._too_warm_count

    def get_comfort_percentage(self) -> float:
        """
        Calculate comfort percentage: 100 * Just Right / Total.
        Safely returns 0.0 if total votes is zero.
        """
        total = self.get_total_count()
        if total == 0:
            return 0.0
        return (100.0 * self._just_right_count) / float(total)

    def get_trend(self) -> str:
        """
        Determine overall trend display string:
        - Blank string ("") if zero votes
        - 'Just Right leads' if just_right is strictly highest
        - 'Trend: Too Cold' if too_cold is strictly highest
        - 'Trend: Too Warm' if too_warm is strictly highest
        - 'Trend: Mixed' if there is a tie for the leading vote
        All strings are <= 16 characters for LCD 1602 line 2.
        """
        total = self.get_total_count()
        if total == 0:
            return ""

        jr = self._just_right_count
        tc = self._too_cold_count
        tw = self._too_warm_count
        max_votes = max(jr, tc, tw)

        leaders = []
        if jr == max_votes:
            leaders.append('just_right')
        if tc == max_votes:
            leaders.append('too_cold')
        if tw == max_votes:
            leaders.append('too_warm')

        if len(leaders) > 1:
            return "Trend: Mixed"
        elif leaders[0] == 'just_right':
            return "Just Right leads"
        elif leaders[0] == 'too_cold':
            return "Trend: Too Cold"
        elif leaders[0] == 'too_warm':
            return "Trend: Too Warm"
        return "Trend: Mixed"

    def reset(self) -> None:
        """Clear all three vote counts back to zero."""
        self._just_right_count = 0
        self._too_cold_count = 0
        self._too_warm_count = 0
