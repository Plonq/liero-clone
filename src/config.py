import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

config = {
    "settings": {
        "sound": {
            "master_volume": 1,
            "effects_volume": 1,
            "music_volume": 1,
        }
    }
}

with open(ROOT_DIR / "config/weapons.json", "rb") as f:
    config["weapons"] = json.load(f)
