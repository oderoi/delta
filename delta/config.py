import os
from pathlib import Path

HOME = Path.home()
DELTA_DIR = HOME / ".delta"
MODELS_DIR = DELTA_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_CONFIG_FILE = DELTA_DIR / "config.json"  # Renamed for clarity