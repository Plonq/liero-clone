import time
import pygame as pg

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
