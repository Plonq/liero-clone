from pathlib import Path

import pygame as pg

from src.engine.sprite import load_sprites

ROOT_DIR = Path(__file__).parent.parent

_assets = {}


def init():
    load_sprites(ROOT_DIR / "assets/images/entities")
    _assets["images"] = {
        "maps": {
            "default": (
                _get_image("maps/default/main.png"),
                _get_image("maps/default/obstacles.png"),
            )
        },
        "gfx": {"explosions": {"small": _get_image("gfx/explosion-small.png")}},
        "projectiles": {"basic": _get_image("weapons/basic-projectile.png")},
    }


def _get_image(relative_path, alpha=True):
    img = pg.image.load(ROOT_DIR / "assets/images/" / relative_path)
    if alpha:
        img = img.convert_alpha()
    else:
        img = img.convert()
    return img


def get_asset(*args):
    cur = _assets
    for arg in args:
        cur = cur[arg]
    return cur


def get_image(*args):
    return get_asset("images", *args)
