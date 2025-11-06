import json
import os
from typing import Optional


class ScoreManager:
    """Manages high score persistence across game sessions."""

    def __init__(self, save_file: str = "highscore.json") -> None:
        """Initialize score manager and load existing high score.

        Args:
            save_file: Path to JSON file for storing high score
        """
        self.save_file: str = save_file
        self.best_score: int = self._load_best_score()

    def _load_best_score(self) -> int:
        """Load the best score from save file.

        Returns:
            Best score from file, or 0 if file doesn't exist or is invalid
        """
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r") as f:
                    data: dict = json.load(f)
                    return data.get("best_score", 0)
            except (json.JSONDecodeError, IOError):
                return 0
        return 0

    def _save_best_score(self) -> None:
        """Save the current best score to file."""
        try:
            with open(self.save_file, "w") as f:
                json.dump({"best_score": self.best_score}, f)
        except IOError:
            pass  # Fail silently if we can't save

    def update_best_score(self, current_score: int) -> bool:
        """Update best score if current score is higher.

        Args:
            current_score: Score to compare against best score

        Returns:
            True if best score was updated, False otherwise
        """
        if current_score > self.best_score:
            self.best_score = current_score
            self._save_best_score()
            return True
        return False

    def get_best_score(self) -> int:
        """Get the current best score.

        Returns:
            The highest score achieved
        """
        return self.best_score
