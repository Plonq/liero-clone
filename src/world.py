import pygame as pg
from pygame.math import Vector2

from src.utils import clamp


class World:
    def __init__(self, game):
        self.game = game
        image = self.game.assets.world_map
        image = image.convert_alpha()
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

    def update(self):
        self._update_offset()

    def draw(self, surf):
        surf.fill((53, 29, 15))
        for map_boundary_rect in self.map_boundary_rects:
            pg.draw.rect(surf, (0, 0, 0), map_boundary_rect)
        surf.blit(self.image, (-self.offset.x, -self.offset.y))
        self.game.player.draw(self.game.display, self.offset)

    def _update_offset(self):
        self.true_offset[0] += (
            self.game.player.x
            - self.true_offset[0]
            - self.game.window.display_size[0] / 2
            + self.game.player.width // 2
        ) / 15
        self.true_offset[1] += (
            self.game.player.y
            - self.true_offset[1]
            - self.game.window.display_size[1] / 2
            + self.game.player.height // 2
        ) / 15
        # Clamp to prevent camera going outside map
        self.true_offset[0] = clamp(
            self.true_offset[0], 0, self.size[0] - self.game.window.display_size[0]
        )
        self.true_offset[1] = clamp(
            self.true_offset[1], 0, self.size[1] - self.game.window.display_size[1]
        )
        self.offset = Vector2(int(self.true_offset[0]), int(self.true_offset[1]))

    def get_visible_rect(self):
        return pg.Rect(
            self.game.offset.x,
            self.game.offset.y,
            self.game.window.display_size[0],
            self.game.window.display_size[1],
        )

    def generate_mask(self):
        return pg.mask.from_surface(self.image)

    def destroy_terrain(self, location, radius):
        color = (0, 0, 0, 0)
        pg.draw.circle(self.image, color, location, radius)
        self.mask = self.generate_mask()
