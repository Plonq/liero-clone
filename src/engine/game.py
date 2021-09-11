import time
from timeit import timeit

import pygame as pg
from pygame.math import Vector2

from src.engine.input import process_input_events

clock = pg.time.Clock()

WINDOW_SIZE = (1216, 800)
DISPLAY_SIZE = (608, 400)
FPS = 60


class Game:
    def __init__(self, window_size, display_size, title):
        self.dt = 0
        self.last_time = time.time()
        self.window_size = window_size
        self.display_size = display_size
        pg.init()
        pg.display.set_caption(title)
        self.screen = pg.display.set_mode(self.window_size, 0, 32)
        self.display = pg.Surface(self.display_size)
        self.game_objects = []
        self.iterations = 0

    def add_object(self, game_object):
        self.game_objects.append(game_object)

    def remove_object(self, game_object):
        self.game_objects.remove(game_object)

    def run(self):
        while True:
            self.dt = (time.time() - self.last_time) * 60
            self.last_time = time.time()
            self._process_events()
            self._update()
            self._draw()
            self._render_frame()

    def _process_events(self):
        process_input_events()

    def _update(self):
        for game_object in self.game_objects:
            game_object.update(self.dt)

    def _draw(self):
        for game_object in self.game_objects:
            game_object.draw(self.display)

    def _render_frame(self):
        self.screen.blit(pg.transform.scale(self.display, self.window_size), (0, 0))
        pg.display.update()
        clock.tick(FPS)

    def quit(self):
        pg.quit()
        exit()

    def get_mouse_pos(self):
        window_pos = pg.mouse.get_pos()
        ratio_x = self.display_size[0] / self.window_size[0]
        ratio_y = self.display_size[1] / self.window_size[1]
        return Vector2(window_pos[0] * ratio_x, window_pos[1] * ratio_y)


class GameObject:
    def update(self, dt):
        pass

    def draw(self, surface):
        pass
