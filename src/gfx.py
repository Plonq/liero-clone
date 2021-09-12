from src.assets import get_image
from src.engine.gfx import Effect


class Explosion(Effect):
    variants = {
        "small": {
            "spritesheet_img_path": "gfx/explosion-small.png",
            "image_count": 7,
            "frame_size": 14,
            "lifespan": 0.2,
        }
    }

    def __init__(self, game, position, size="small"):
        super().__init__(
            game,
            position=position,
            spritesheet_img=get_image(self.variants[size]["spritesheet_img_path"]),
            image_count=self.variants[size]["image_count"],
            frame_size=self.variants[size]["frame_size"],
            lifespan=self.variants[size]["lifespan"],
        )
