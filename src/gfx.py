from src.assets import get_image
from src.engine.gfx import Effect
from src.engine.sprite import SpriteStrip


class SmallExplosion(Effect):
    def __init__(self, game, position):
        super().__init__(
            game,
            position=position,
            sprite_strip=SpriteStrip(img=get_image("gfx/explosion-small.png")),
            lifespan=0.2,
        )
