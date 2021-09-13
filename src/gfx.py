from src.assets import assets
from src.engine.gfx import Effect


class SmallExplosion(Effect):
    def __init__(self, game, position):
        super().__init__(
            game,
            position=position,
            sprite_strip=assets["img"]["explosions"]["small"],
            lifespan=0.2,
        )
