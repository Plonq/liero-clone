import time

import pygame as pg
from pygame.math import Vector2

from .input import process_input_events

clock = pg.time.Clock()

WINDOW_SIZE = (1216, 800)
DISPLAY_SIZE = (608, 400)
FPS = 60


class Game:
    def __init__(self, window_size, display_size, title):
        pg.mixer.pre_init(44100, -16, 2, 2048)
        pg.init()
        pg.display.set_caption(title)
        pg.mixer.set_num_channels(50)
        self.dt = 0
        self.last_time = time.time()
        self.window_size = window_size
        self.display_size = display_size
        self.screen = pg.display.set_mode(self.window_size, 0, 32)
        self.display = pg.Surface(self.display_size)
        self.game_objects = []
        self.offset = Vector2(0, 0)

    def add_object(self, game_object):
        self.game_objects.append(game_object)

    def remove_object(self, game_object):
        self.game_objects.remove(game_object)

    def run(self):
        while True:
            self.dt = time.time() - self.last_time
            self.last_time = time.time()
            self._process_events()
            self.update_offset(self.dt)
            self.pre_update(self.dt)
            self._update(self.dt, self.offset)
            self.post_update(self.dt)
            self._draw(self.display, self.offset)
            self._render_frame()

    def _process_events(self):
        process_input_events()

    def pre_update(self, dt):
        """Called prior to update and draw of game objects."""
        pass

    def _update(self, dt, offset):
        for _, game_object in sorted(enumerate(self.game_objects), reverse=True):
            game_object.update(dt, offset)

    def post_update(self, dt):
        """Called after update and before draw."""
        pass

    def _draw(self, surface, offset):
        for game_object in self.game_objects:
            game_object.draw(surface, offset)

    def update_offset(self, dt):
        """Sub-classes should override this and set self.offset to a Vector2, if required."""
        pass

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

    def get_direction_to_mouse(self, position):
        mouse_pos = self.get_mouse_pos()
        return (mouse_pos + self.offset - position).normalize()


class GameObject:
    def update(self, dt, offset):
        pass

    def draw(self, surface, offset):
        pass
