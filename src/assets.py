from pathlib import Path

import pygame as pg

from src.engine.entity import load_animation_data

ROOT_DIR = Path(__file__).parent.parent

world_map = None
basic_projectile = None


def init():
    global world_map
    global basic_projectile
    load_animation_data(ROOT_DIR / "assets/images/entities")
    world_map = pg.image.load(ROOT_DIR / "assets/images/map.png").convert_alpha()
    basic_projectile = pg.image.load(
        ROOT_DIR / "assets/images/weapons/basic-projectile.png"
    ).convert_alpha()
