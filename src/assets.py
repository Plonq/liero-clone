from pathlib import Path

import pygame as pg

from src.engine.entity import load_sprites
from src.engine.sprite import SpriteStrip

ROOT_DIR = Path(__file__).parent.parent

_asset_cache = {"images": {}}
assets = {"img": {}, "sound": {}, "font": {}}


def init():
    load_sprites(ROOT_DIR / "assets/images/entities")
    # Images
    assets["img"]["explosions"] = {
        "small": SpriteStrip(get_image("gfx/explosion-small.png"))
    }
    # Sounds
    ex4 = pg.mixer.Sound(ROOT_DIR / "assets/sounds/Explosion1.wav")
    ex4.set_volume(0.1)
    assets["sound"]["explosions"] = {"small": ex4}
    # Fonts
    assets["font"]["small"] = pg.image.load(
        ROOT_DIR / "assets/fonts/small_font.png"
    ).convert_alpha()
    assets["font"]["large"] = pg.image.load(
        ROOT_DIR / "assets/fonts/large_font.png"
    ).convert()


def get_image(relative_path, alpha=True):
    if relative_path not in _asset_cache["images"]:
        img = pg.image.load(ROOT_DIR / "assets/images/" / relative_path)
        if alpha:
            img = img.convert_alpha()
        else:
            img = img.convert()
        _asset_cache["images"][relative_path] = img
    return _asset_cache["images"][relative_path]
