import time

import pygame as pg
from pygame.math import Vector2

from src.assets import Assets
from src.input import Input
from src.world import World

clock = pg.time.Clock()

WINDOW_SIZE = (1216, 800)
DISPLAY_SIZE = (608, 400)


class Game:
    def __init__(self):
        self.dt = 0
        self.last_time = time.time()
        self.window_size = WINDOW_SIZE
        self.display_size = DISPLAY_SIZE
        pg.init()
        pg.display.set_caption("Liero Clone")
        self.screen = pg.display.set_mode(self.window_size, 0, 32)
        self.display = pg.Surface(self.display_size)
        self.assets = Assets()
        self.input = Input(self)
        self.world = World(self)

    def _update(self):
        self.input.update()
        self.world.update()
        self._render_frame()

    def _render_frame(self):
        self.dt = (time.time() - self.last_time) * 60
        self.last_time = time.time()
        self.screen.blit(pg.transform.scale(self.display, self.window_size), (0, 0))
        pg.display.update()
        clock.tick(60)

    def _draw(self):
        self.world.draw(self.display)

    def run(self):
        while True:
            self._update()
            self._draw()

    def get_mouse_pos(self):
        window_pos = pg.mouse.get_pos()
        ratio_x = self.display_size[0] / self.window_size[0]
        ratio_y = self.display_size[1] / self.window_size[1]
        return Vector2(window_pos[0] * ratio_x, window_pos[1] * ratio_y)


if __name__ == "__main__":
    Game().run()
