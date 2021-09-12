import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

with open(ROOT_DIR / "config/weapons.json", "rb") as f:
    weapons = json.load(f)
