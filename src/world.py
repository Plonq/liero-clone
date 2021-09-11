import random

import pygame as pg
from pygame.math import Vector2

from src.engine.game import GameObject
from src.engine.input import is_action_pressed
from src.player import Player
from src.engine.utils import clamp


class World(GameObject):
    def __init__(self, game):
        self.game = game
        image = self.game.assets.world_map
        self.image = image
        self.mask = self.generate_mask()
        self.size = image.get_size()
        self.true_offset = [0, 0]
        self.offset = Vector2(0)
        self.map_boundary_rects = (
            pg.Rect(-1, -1, self.size[0], 1),
            pg.Rect(-1, -1, 1, self.size[1]),
            pg.Rect(self.size[0], -1, 1, self.size[1]),
            pg.Rect(-1, self.size[1], self.size[0], 1),
        )
        self.player = Player(game)
        self.projectiles = []

    def update(self, dt):
        self._update_offset()
        if is_action_pressed("spawn"):
            if not self.player.alive:
                self.spawn()
        self.player.update(self.map_boundary_rects, self.mask, dt)
        self._update_projectiles(dt)

    def draw(self, surface):
        surface.fill((53, 29, 15))
        for map_boundary_rect in self.map_boundary_rects:
            pg.draw.rect(surface, (0, 0, 0), map_boundary_rect)
        surface.blit(self.image, (-self.offset.x, -self.offset.y))
        self.player.draw(self.game.display, self.offset)
        self._draw_projectiles(surface, self.offset)

    def _update_offset(self):
        self.true_offset[0] += (
            self.player.x
            - self.true_offset[0]
            - self.game.display_size[0] / 2
            + self.player.width // 2
        ) / 15
        self.true_offset[1] += (
            self.player.y
            - self.true_offset[1]
            - self.game.display_size[1] / 2
            + self.player.height // 2
        ) / 15
        # Clamp to prevent camera going outside map
        self.true_offset[0] = clamp(
            self.true_offset[0], 0, self.size[0] - self.game.display_size[0]
        )
        self.true_offset[1] = clamp(
            self.true_offset[1], 0, self.size[1] - self.game.display_size[1]
        )
        self.offset = Vector2(int(self.true_offset[0]), int(self.true_offset[1]))

    def _update_projectiles(self, dt):
        for i, projectile in sorted(enumerate(self.projectiles), reverse=True):
            projectile.update(dt)
            if not pg.Rect(0, 0, *self.size).collidepoint(
                projectile.position.x, projectile.position.y
            ):
                self.projectiles.pop(i)

    def _draw_projectiles(self, surface, offset):
        for projectile in self.projectiles:
            projectile.draw(surface, offset)

    def get_visible_rect(self):
        return pg.Rect(
            self.offset.x,
            self.offset.y,
            self.game.display_size[0],
            self.game.display_size[1],
        )

    def generate_mask(self):
        return pg.mask.from_surface(self.image)

    def destroy_terrain(self, location, radius):
        color = (0, 0, 0, 0)
        pg.draw.circle(self.image, color, location, radius)
        self.mask = self.generate_mask()

    def spawn(self):
        position = Vector2(
            random.randint(
                self.player.width, self.game.display_size[0] - self.player.width
            ),
            random.randint(
                self.player.height, self.game.display_size[1] - self.player.height
            ),
        )
        self.destroy_terrain(position, radius=self.player.height * 0.8)
        self.player.x, self.player.y = position
        self.player.alive = True
