from pathlib import Path

import pygame as pg

from src.engine.sprite import load_sprites

ROOT_DIR = Path(__file__).parent.parent

_asset_cache = {"images": {}, "maps": {}, "gfx": {}, "weapons": {}}
_assets = {}


def init():
    global _assets
    load_sprites(ROOT_DIR / "assets/images/entities")
    _assets = {
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
    if relative_path not in _asset_cache["images"]:
        img = _asset_cache["images"][relative_path] = pg.image.load(
            ROOT_DIR / "assets/images/" / relative_path
        )
        if alpha:
            img = img.convert_alpha()
        else:
            img = img.convert()
        _asset_cache["images"][relative_path] = img
    return _asset_cache["images"][relative_path]


def get_asset(*args):
    cur = _assets
    for arg in args:
        cur = cur[arg]
    return cur
