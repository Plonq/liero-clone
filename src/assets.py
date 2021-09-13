from pathlib import Path

import pygame as pg

from src.engine.entity import load_sprites
from src.engine.sprite import SpriteStrip

ROOT_DIR = Path(__file__).parent.parent

_asset_cache = {"images": {}}
assets = {"img": {}}


def init():
    load_sprites(ROOT_DIR / "assets/images/entities")
    assets["img"]["explosions"] = {
        "small": SpriteStrip(get_image("gfx/explosion-small.png"))
    }


def get_image(relative_path, alpha=True):
    if relative_path not in _asset_cache["images"]:
        img = pg.image.load(ROOT_DIR / "assets/images/" / relative_path)
        if alpha:
            img = img.convert_alpha()
        else:
            img = img.convert()
        _asset_cache["images"][relative_path] = img
    return _asset_cache["images"][relative_path]
