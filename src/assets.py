from pathlib import Path

import pygame as pg

from src.engine.sprite import load_sprites

ROOT_DIR = Path(__file__).parent.parent

_asset_cache = {"images": {}}


def init():
    load_sprites(ROOT_DIR / "assets/images/entities")


def get_image(relative_path, alpha=True):
    if relative_path not in _asset_cache["images"]:
        img = pg.image.load(ROOT_DIR / "assets/images/" / relative_path)
        if alpha:
            img = img.convert_alpha()
        else:
            img = img.convert()
        _asset_cache["images"][relative_path] = img
    return _asset_cache["images"][relative_path]
