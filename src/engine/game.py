import time

import pygame as pg
from pygame.math import Vector2

from .input import process_input_events, update_input_states

clock = pg.time.Clock()

FPS = 60


class Game:
    def __init__(self, window_size, display_size, title):
        pg.mixer.pre_init(44100, -16, 2, 2048)
        pg.init()
        pg.display.set_caption(title)
        pg.mixer.set_num_channels(512)
        self.dt = 0
        self.last_time = time.time()
        self.orig_window_size = window_size
        self.monitor_size = (pg.display.Info().current_w, pg.display.Info().current_h)
        self.window_size = window_size
        self.display_size = display_size
        self.fullscreen = False
        self.screen = pg.display.set_mode(self.window_size, pg.RESIZABLE, 32)
        self.display = pg.Surface(self.display_size)
        self.game_objects = []
        self.offset = Vector2(0, 0)

    def add_object(self, game_object):
        self.game_objects.append(game_object)

    def remove_object(self, game_object):
        try:
            self.game_objects.remove(game_object)
        except ValueError:
            # Don't care if it doesn't exist
            pass

    def run(self):
        while True:
            self.dt = time.time() - self.last_time
            self.last_time = time.time()
            self._process_events()
            self.update_offset(self.dt)
            self.pre_update(self.dt, self.offset)
            self._update(self.dt, self.offset)
            self.post_update(self.dt, self.offset)
            self._draw(self.display, self.offset)
            self._render_frame()

    def _process_events(self):
        update_input_states()
        input_events = []
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.VIDEORESIZE:
                if not self.fullscreen:
                    self.window_size = (event.w, event.h)
                    self.screen = pg.display.set_mode(
                        self.window_size, pg.RESIZABLE, 32
                    )
            elif event.type in [
                pg.MOUSEBUTTONUP,
                pg.MOUSEBUTTONDOWN,
                pg.MOUSEMOTION,
                pg.KEYUP,
                pg.KEYDOWN,
            ]:
                input_events.append(event)
        process_input_events(self, input_events)

    def pre_update(self, dt, offset):
        """Called prior to update and draw of game objects."""
        pass

    def _update(self, dt, offset):
        for _, game_object in sorted(enumerate(self.game_objects), reverse=True):
            game_object.update(dt, offset)

    def post_update(self, dt, offset):
        """Called after update and before draw."""
        pass

    def _draw(self, surface, offset):
        for game_object in sorted(self.game_objects, key=lambda obj: obj.z_index):
            game_object.draw(surface, offset)

    def update_offset(self, dt):
        """Sub-classes should override this and set self.offset to a Vector2, if required."""
        pass

    def _render_frame(self):
        self.screen.blit(pg.transform.scale(self.display, self.window_size), (0, 0))
        pg.display.update()
        clock.tick(FPS)

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.window_size = self.monitor_size
            self.screen = pg.display.set_mode(self.window_size, pg.FULLSCREEN, 32)
        else:
            self.window_size = self.orig_window_size
            self.screen = pg.display.set_mode(self.window_size, pg.RESIZABLE, 32)

    def quit(self):
        pg.quit()
        exit()

    def get_mouse_pos(self):
        window_pos = pg.mouse.get_pos()
        ratio_x = self.display_size[0] / self.window_size[0]
        ratio_y = self.display_size[1] / self.window_size[1]
        return Vector2(window_pos[0] * ratio_x, window_pos[1] * ratio_y)

    def get_display_mouse_pos(self, window_pos):
        ratio_x = self.display_size[0] / self.window_size[0]
        ratio_y = self.display_size[1] / self.window_size[1]
        return Vector2(window_pos[0] * ratio_x, window_pos[1] * ratio_y)

    def get_direction_to_mouse(self, position):
        mouse_pos = self.get_mouse_pos()
        return (mouse_pos + self.offset - position).normalize()


class GameObject:
    z_index = 0

    def update(self, dt, offset):
        pass

    def draw(self, surface, offset):
        pass
