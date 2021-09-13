from .game import GameObject
from .sprite import SpriteSheetExtractor
from .utils import blit_centered


class Effect(GameObject):
    """Generic class for a once-off graphical effect, like an explosion."""

    def __init__(self, game, sprite_strip, position, lifespan):
        self.game = game
        self.sprite_strip = sprite_strip
        self.position = position
        self.lifespan = lifespan
        self.frame_index = 0
        self.time_since_first_frame = 0

    def update(self, dt, offset):
        self.time_since_first_frame += dt
        frame_index = int(
            self.time_since_first_frame / (self.lifespan / self.sprite_strip.frames)
        )
        if frame_index >= self.sprite_strip.frames:
            self.game.remove_object(self)
        else:
            self.frame_index = frame_index

    def draw(self, surface, offset):
        blit_centered(
            self.sprite_strip.get_frame(self.frame_index),
            surface,
            self.position - offset,
        )
