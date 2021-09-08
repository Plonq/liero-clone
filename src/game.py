from time import time

import pygame as pg
from pygame.math import Vector2

from src.assets import Assets
from src.world import World
from src.player import Player
from src.utils import clamp
from src.weapons import MachineGun

clock = pg.time.Clock()


class Game:
    true_offset = [0, 0]
    last_time = time()
    display_size = (608, 400)
    offset = Vector2(0, 0)

    def __init__(self, screen):
        self.assets = Assets()
        self.world = World(self)

        pg.display.set_caption("Liero Clone")
        self.screen = screen
        self.display = pg.Surface(self.display_size)

        # Set up map
        map_size = self.world.size
        self.map_boundary_rects = (
            pg.Rect(0, 0, map_size[0], 1),
            pg.Rect(0, 0, 1, map_size[1]),
            pg.Rect(map_size[0] - 1, 0, 1, map_size[1]),
            pg.Rect(0, map_size[1] - 1, map_size[0], 1),
        )

        # Set up player
        self.player = Player(x=300, y=300)
        self.world.destroy_terrain(
            (self.player.x, self.player.y), radius=self.player.height * 0.8
        )
        self.firing_at = None
        self.player.current_weapon = MachineGun()

    def run(self):
        while True:
            dt = (time() - self.last_time) * 60
            self.last_time = time()
            self.next_frame(dt)
            self.process_events(pg.event.get())
            window_size = (self.screen.get_width(), self.screen.get_height())
            self.screen.blit(pg.transform.scale(self.display, window_size), (0, 0))
            pg.display.update()
            clock.tick(60)

    def next_frame(self, dt):
        self.display.fill((53, 29, 15))

        self._update_offset()
        visible_rect = pg.Rect(
            self.offset.x, self.offset.y, self.display_size[0], self.display_size[1]
        )

        # Map and player
        for map_boundary_rect in self.map_boundary_rects:
            pg.draw.rect(self.display, (0, 0, 0), map_boundary_rect)

        self.world.draw(self.display, self.offset)

        self.player.update(self.map_boundary_rects, self.world.mask, dt)
        self.player.draw(self.display, self.offset)

        # Weapons
        if self.firing_at:
            self.player.current_weapon.fire(
                self.player.position, self.firing_at + self.offset
            )
        self.player.current_weapon.update(visible_rect, dt)
        self.player.current_weapon.draw(self.display, self.offset)

    def _update_offset(self):
        self.true_offset[0] += (
            self.player.x - self.true_offset[0] - 300 + self.player.width // 2
        ) / 15
        self.true_offset[1] += (
            self.player.y - self.true_offset[1] - 200 + self.player.height // 2
        ) / 15
        # Clamp to prevent camera going outside map
        self.true_offset[0] = clamp(
            self.true_offset[0], 0, self.world.size[0] - self.display_size[0]
        )
        self.true_offset[1] = clamp(
            self.true_offset[1], 0, self.world.size[1] - self.display_size[1]
        )
        self.offset = Vector2(int(self.true_offset[0]), int(self.true_offset[1]))

    def process_events(self, events):
        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == pg.BUTTON_LEFT:
                    self.firing_at = self.correct_mouse_pos(event.pos)
                if event.button == pg.BUTTON_RIGHT:
                    target = self.correct_mouse_pos(event.pos)
                    self.dig(toward=target)
            if event.type == pg.MOUSEMOTION and self.firing_at:
                self.firing_at = self.correct_mouse_pos(event.pos)
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                self.firing_at = None

    def dig(self, toward):
        player_pos = Vector2(self.player.x, self.player.y)
        direction = (toward + self.offset - player_pos).normalize()
        dig_pos = player_pos + (direction * 5)
        self.world.destroy_terrain(dig_pos, self.player.height * 0.8)

    def correct_mouse_pos(self, original_pos):
        ratio_x = self.display_size[0] / self.screen.get_width()
        ratio_y = self.display_size[1] / self.screen.get_height()
        display_pos = Vector2(original_pos[0] * ratio_x, original_pos[1] * ratio_y)
        return display_pos
