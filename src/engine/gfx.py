from .game import GameObject
from .sprite import SpriteSheetExtractor
from .utils import blit_centered


class Effect(GameObject):
    """Generic class for a once-off graphical effect, like an explosion."""

    def __init__(self, game, ss, position, lifespan):
        self.game = game
        self.ss = ss
        self.lifespan = lifespan
        # self.image_count = image_count
        # self.images = SpriteSheet(spritesheet_img).load_strip(
        #     (0, 0, frame_size, frame_size), image_count=image_count
        # )
        self.image = ss.get_frame(0)
        self.position = position
        self.current_image = 0
        self.time_since_first_frame = 0
        # self.frame_lifespan = lifespan / image_count

    def update(self, dt, offset):
        self.time_since_first_frame += dt
        next_img = self.ss.get_frame_by_lifespan(
            self.time_since_first_frame, self.lifespan
        )
        if next_img is None:
            self.game.remove_object(self)
        else:
            self.image = next_img

    def draw(self, surface, offset):
        blit_centered(self.image, surface, self.position - offset)
