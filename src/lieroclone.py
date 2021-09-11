import pygame as pg

from src.assets import Assets
from src.engine.game import Game
from src.world import World

clock = pg.time.Clock()

WINDOW_SIZE = (1216, 800)
DISPLAY_SIZE = (608, 400)


class LieroClone(Game):
    def __init__(self):
        super().__init__(WINDOW_SIZE, DISPLAY_SIZE, "Liero Clone")
        self.assets = Assets()
        self.world = World(self)
        self.add_object(self.world)


if __name__ == "__main__":
    LieroClone().run()
