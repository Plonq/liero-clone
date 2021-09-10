from pathlib import Path

import pygame as pg

from src.engine import load_animation_data

ROOT_DIR = Path(__file__).parent.parent


class Assets:
    def __init__(self):
        load_animation_data(ROOT_DIR / "assets/images/entities")
        self.world_map = pg.image.load(
            ROOT_DIR / "assets/images/map.png"
        ).convert_alpha()
        self.basic_projectile = pg.image.load(
            ROOT_DIR / "assets/images/weapons/basic-projectile.png"
        ).convert_alpha()
