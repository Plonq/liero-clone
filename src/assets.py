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
    assets["sound"]["explosions"] = {}
    for i in range(1, 11):
        assets["sound"]["explosions"][i] = pg.mixer.Sound(
            ROOT_DIR / f"assets/sounds/Explosion{i}.wav"
        )
    assets["sound"]["death"] = pg.mixer.Sound(ROOT_DIR / "assets/sounds/HitGore3.wav")
    assets["sound"]["worm-impact"] = pg.mixer.Sound(
        ROOT_DIR / "assets/sounds/worm-impact.wav"
    )

    assets["sound"]["gunshots"] = {}
    for i in range(1, 12):
        assets["sound"]["gunshots"][i] = pg.mixer.Sound(
            ROOT_DIR / f"assets/sounds/Gunshot{i}.wav"
        )

    assets["sound"]["grunts"] = {}
    for i in range(1, 9):
        assets["sound"]["grunts"][i] = pg.mixer.Sound(
            ROOT_DIR / f"assets/sounds/Male{i}.wav"
        )
    assets["sound"]["slash"] = pg.mixer.Sound(ROOT_DIR / "assets/sounds/Slash1.wav")

    # Fonts
    assets["font"]["small"] = pg.image.load(
        ROOT_DIR / "assets/fonts/small_font.png"
    ).convert_alpha()
    assets["font"]["large"] = pg.image.load(
        ROOT_DIR / "assets/fonts/large_font.png"
    ).convert()
    assets["font"]["large"].set_colorkey((0, 0, 0))


def get_image(relative_path, alpha=True):
    if relative_path not in _asset_cache["images"]:
        img = pg.image.load(ROOT_DIR / "assets/images/" / relative_path)
        if alpha:
            img = img.convert_alpha()
        else:
            img = img.convert()
        _asset_cache["images"][relative_path] = img
    return _asset_cache["images"][relative_path]
