from pathlib import Path

import pygame as pg

from src.engine.entity import load_animation_data

ROOT_DIR = Path(__file__).parent.parent

world_map = None
world_obstacles = None
basic_projectile = None


def init():
    global world_map
    global world_obstacles
    global basic_projectile
    load_animation_data(ROOT_DIR / "assets/images/entities")
    world_map = pg.image.load(
        ROOT_DIR / "assets/images/maps/default/main.png"
    ).convert_alpha()
    world_obstacles = pg.image.load(
        ROOT_DIR / "assets/images/maps/default/obstacles.png"
    ).convert_alpha()
    basic_projectile = pg.image.load(
        ROOT_DIR / "assets/images/weapons/basic-projectile.png"
    ).convert_alpha()
