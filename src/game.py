import random
from time import time

import pygame as pg
from pygame.math import Vector2

from src.constants import ROOT_DIR
from src.engine import DestroyableMap, Entity, load_animation_data
from src.utils import clamp

clock = pg.time.Clock()


class Game:
    true_offset = [0, 0]
    last_time = time()
    display_size = (608, 400)
    offset = Vector2(0, 0)

    def __init__(self, screen):
        pg.display.set_caption("Liero Clone")
        self.screen = screen
        self.display = pg.Surface(self.display_size)

        # Set up map
        self.game_map = DestroyableMap(ROOT_DIR / "assets/images/map.png")
        map_size = self.game_map.size
        self.map_boundary_rects = (
            pg.Rect(0, 0, map_size[0], 1),
            pg.Rect(0, 0, 1, map_size[1]),
            pg.Rect(map_size[0] - 1, 0, 1, map_size[1]),
            pg.Rect(0, map_size[1] - 1, map_size[0], 1),
        )

        # Set up player
        load_animation_data(ROOT_DIR / "assets/images/entities")
        self.player = Entity("player", x=300, y=300, width=12, height=14)
        self.game_map.destroy_terrain(
            (self.player.x, self.player.y), radius=self.player.height * 0.8
        )
        self.firing_at = None
        self.current_weapon = MachineGun()

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

        self.game_map.draw(self.display, self.offset)

        self.player.update(self.map_boundary_rects, self.game_map.mask, dt)
        self.player.draw(self.display, self.offset)

        # Weapons
        if self.firing_at:
            self.current_weapon.fire(self.player.position, self.firing_at + self.offset)
        self.current_weapon.update(visible_rect, dt)
        self.current_weapon.draw(self.display, self.offset)

    def _update_offset(self):
        self.true_offset[0] += (
            self.player.x - self.true_offset[0] - 300 + self.player.width // 2
        ) / 15
        self.true_offset[1] += (
            self.player.y - self.true_offset[1] - 200 + self.player.height // 2
        ) / 15
        # Clamp to prevent camera going outside map
        self.true_offset[0] = clamp(
            self.true_offset[0], 0, self.game_map.size[0] - self.display_size[0]
        )
        self.true_offset[1] = clamp(
            self.true_offset[1], 0, self.game_map.size[1] - self.display_size[1]
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
        direction = (Vector2(toward) - player_pos).normalize()
        dig_pos = player_pos + (direction * 5)
        self.game_map.destroy_terrain(dig_pos, self.player.height * 0.8)

    def correct_mouse_pos(self, original_pos):
        ratio_x = self.display_size[0] / self.screen.get_width()
        ratio_y = self.display_size[1] / self.screen.get_height()
        display_pos = Vector2(original_pos[0] * ratio_x, original_pos[1] * ratio_y)
        return display_pos


class MachineGun:
    def __init__(self):
        self.image = pg.Surface((1, 1))
        self.image.fill((255, 255, 255))
        self.cooldown = 4
        self.bullet_speed = 2

        self.bullets = []
        self.current_cooldown = self.cooldown

    def fire(self, start_pos, target_pos):
        if self.current_cooldown == 0:
            jitter = random.randrange(-15, 15)
            direction = (target_pos - start_pos).normalize()
            # direction.rotate_ip(jitter)
            start_pos = start_pos + (direction * 14)
            self.bullets.append([start_pos, direction])
            self.current_cooldown = self.cooldown
        else:
            self.current_cooldown -= 1

    def update(self, visible_rect, dt):
        for i, bullet in sorted(enumerate(self.bullets), reverse=True):
            movement = bullet[1] * self.bullet_speed * dt
            bullet[0] += movement
            if not visible_rect.collidepoint(bullet[0].x, bullet[0].y):
                self.bullets.pop(i)

    def draw(self, surface, offset):
        for i, bullet in sorted(enumerate(self.bullets), reverse=True):
            surface.blit(self.image, bullet[0] - offset)
