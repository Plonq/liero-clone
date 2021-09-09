import time
import pygame as pg
from pygame.math import Vector2

clock = pg.time.Clock()


class Window:
    window_size = (1216, 800)
    display_size = (608, 400)

    def __init__(self, game):
        self.game = game
        self.dt = 0
        self.last_time = time.time()
        pg.init()
        pg.display.set_caption("Liero Clone")
        self.screen = pg.display.set_mode(self.window_size, 0, 32)
        self.display = pg.Surface(self.display_size)

    def render_frame(self):
        self.dt = (time.time() - self.last_time) * 60
        self.last_time = time.time()
        self.screen.blit(pg.transform.scale(self.display, self.window_size), (0, 0))
        pg.display.update()
        clock.tick(60)

    def get_mouse_pos(self):
        window_pos = pg.mouse.get_pos()
        ratio_x = self.display_size[0] / self.window_size[0]
        ratio_y = self.display_size[1] / self.window_size[1]
        return Vector2(window_pos[0] * ratio_x, window_pos[1] * ratio_y)
