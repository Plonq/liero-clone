import random

import pygame as pg
from pygame.math import Vector2

from src.constants import DISPLAY_SIZE, ROOT_DIR, WINDOW_SIZE
from src.engine import DestroyableMap, Entity, load_animation_data


class Game:
    true_offset = [0, 0]

    def __init__(self):
        load_animation_data(ROOT_DIR / "assets/images/entities")

        self.game_map = DestroyableMap(ROOT_DIR / "assets/images/map.png")
        self.player = Entity("player", x=90, y=50, width=16, height=16)
        self.map_boundary_rects = (
            pg.Rect(0, 0, DISPLAY_SIZE[0], 1),
            pg.Rect(0, 0, 1, DISPLAY_SIZE[1]),
            pg.Rect(DISPLAY_SIZE[0] - 1, 0, 1, DISPLAY_SIZE[1]),
            pg.Rect(0, DISPLAY_SIZE[1] - 1, DISPLAY_SIZE[0], 1),
        )

        # Spawning
        self.game_map.destroy_terrain((self.player.x, self.player.y), self.player.width)

        # Weapons
        self.bullet_img = pg.Surface((1, 1))
        self.bullet_img.fill((255, 255, 255))
        self.firing_at = None
        self.machine_gun_cooldown = 0
        self.machine_gun_bullets = []
        self.bullet_speed = 2

    def next_frame(self, display, dt):
        display.fill((53, 29, 15))

        # Camera follow player
        player_rect = self.player.rect
        # true_offset[0] += (
        #     player_rect.x - true_offset[0] - 300 + player_rect.width // 2
        # ) / 15
        # true_offset[1] += (
        #     player_rect.y - true_offset[1] - 200 + player_rect.height // 2
        # ) / 15
        # Clamp to prevent camera going outside map
        # true_offset[0] = clamp(true_offset[0], 0, game_map.dimensions[0] - DISPLAY_SIZE[0])
        # true_offset[1] = clamp(true_offset[1], 0, game_map.dimensions[1] - DISPLAY_SIZE[1])
        offset = Vector2(int(self.true_offset[0]), int(self.true_offset[1]))
        # Map and player
        for map_boundary_rect in self.map_boundary_rects:
            pg.draw.rect(display, (0, 0, 0), map_boundary_rect)

        self.game_map.draw(display)

        self.player.update(self.map_boundary_rects, self.game_map.mask, dt)
        self.player.draw(display, offset)

        # Weapons
        if self.firing_at:
            if self.machine_gun_cooldown == 0:
                jitter = random.randrange(-15, 15)
                direction = (
                    Vector2(self.firing_at) - Vector2(self.player.x, self.player.y)
                ).normalize()
                # direction.rotate_ip(jitter)
                start_pos = Vector2(self.player.x, self.player.y) + (direction * 14)
                self.machine_gun_bullets.append([start_pos, direction])
                machine_gun_cooldown = 1
            else:
                self.machine_gun_cooldown -= 1

        for i, bullet in sorted(enumerate(self.machine_gun_bullets), reverse=True):
            display.blit(self.bullet_img, bullet[0])
            movement = bullet[1] * self.bullet_speed * dt
            bullet[0] += movement

    def process_events(self, events):
        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == pg.BUTTON_LEFT:
                    self.firing_at = self.mouse_pos_to_display_pos(event.pos)
                if event.button == pg.BUTTON_RIGHT:
                    pos = Vector2(self.player.x, self.player.y)
                    pos.x += 10
                    if self.player.flip:
                        pos.x *= -1
                    self.game_map.destroy_terrain(pos, self.player.height / 1.2)
            if event.type == pg.MOUSEMOTION and self.firing_at:
                self.firing_at = self.mouse_pos_to_display_pos(event.pos)
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                self.firing_at = None

    def mouse_pos_to_display_pos(self, pos):
        ratio_x = DISPLAY_SIZE[0] / WINDOW_SIZE[0]
        ratio_y = DISPLAY_SIZE[1] / WINDOW_SIZE[1]
        return pos[0] * ratio_x, pos[1] * ratio_y
