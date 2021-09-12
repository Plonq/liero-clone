from .game import GameObject
from .sprite import SpriteSheet
from .utils import blit_centered


class Effect(GameObject):
    """Generic class for a once-off graphical effect, like an explosion."""

    def __init__(
        self, game, spritesheet_img, image_count, frame_size, position, lifespan
    ):
        self.game = game
        ss = SpriteSheet(spritesheet_img)
        self.image_count = image_count
        self.images = ss.load_strip(
            (0, 0, frame_size, frame_size), image_count=image_count
        )
        self.image = self.images[0]
        self.position = position
        self.current_image = 0
        self.frame_time = 0
        self.frame_lifespan = lifespan / image_count

    def update(self, dt, offset):
        self.frame_time += dt
        frame = int(self.frame_time / self.frame_lifespan)
        if frame >= len(self.images):
            self.game.remove_object(self)
        else:
            self.image = self.images[frame]

    def draw(self, surface, offset):
        blit_centered(self.image, surface, self.position - offset)
