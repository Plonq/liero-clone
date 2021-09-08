import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

config = {}

with open(ROOT_DIR / "config/weapons") as f:
    config["weapons"] = json.load(f)
