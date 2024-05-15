from pathlib import Path
from typing import Dict
import json
from .storage import EncryptedJSONStorage

class TokenTracker:
    def __init__(self, storage_path: Path = Path.home() / ".m" / "tracking.json"):
        """Initialize the TokenTracker."""
        self.storage = EncryptedJSONStorage(str(storage_path))
        self.tracking_data = self.load_tracking_data()

    def load_tracking_data(self) -> Dict:
        """Load tracking data from the storage file."""
        return self.storage.load() or {}

    def save_tracking_data(self):
        """Save tracking data to the storage file."""
        self.storage.save(self.tracking_data)

    def get_model_usage(self, model_name: str) -> Dict:
        """Get the usage data for a specific model."""
        return self.tracking_data.get(model_name, {"requests": 0, "tokens": 0})

    def update_model_usage(self, model_name: str, tokens: int = 0):
        """Update the usage data for a specific model."""
        model_usage = self.get_model_usage(model_name)
        model_usage["requests"] += 1
        model_usage["tokens"] += tokens

        self.tracking_data[model_name] = model_usage
        self.save_tracking_data()

    def model_exceeds_limits(self, model_name: str, limits: Dict) -> bool:
        """Check if a model exceeds its usage limits.

        Args:
            model_name (str): The name of the model.
            limits (Dict): The usage limits for the model.

        Returns:
            bool: True if any limit is exceeded, False otherwise.
        """
        usage = self.get_model_usage(model_name)

        if limits.get("requests_per_minute") is not None and usage["requests"] > limits["requests_per_minute"]:
            return True

        if limits.get("requests_per_day") is not None and usage["requests"] > limits["requests_per_day"]:
            return True

        if limits.get("tokens_per_minute") is not None and usage["tokens"] > limits["tokens_per_minute"]:
            return True

        if limits.get("tokens_per_day") is not None and usage["tokens"] > limits["tokens_per_day"]:
            return True

        return False
