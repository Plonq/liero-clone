import pygame as pg

from src import assets
from src.engine.game import GameObject


class Map(GameObject):
    def __init__(self, game):
        self.game = game
        image = assets.world_map
        obstacles = assets.world_obstacles
        self.image = image
        self.obstacles = obstacles
        self.destructible_mask = None
        self.indestructible_mask = pg.mask.from_surface(self.obstacles)
        self.update_destructible_mask()
        self.size = image.get_size()
        self.map_boundary_rects = (
            pg.Rect(-1, -1, self.size[0], 1),
            pg.Rect(-1, -1, 1, self.size[1]),
            pg.Rect(self.size[0], -1, 1, self.size[1]),
            pg.Rect(-1, self.size[1], self.size[0], 1),
        )

    def update(self, dt, offset):
        pass

    def draw(self, surface, offset):
        surface.fill((53, 29, 15))
        for map_boundary_rect in self.map_boundary_rects:
            pg.draw.rect(surface, (0, 0, 0), map_boundary_rect)
        surface.blit(self.image, (-offset.x, -offset.y))
        surface.blit(self.obstacles, (-offset.x, -offset.y))

    def update_destructible_mask(self):
        self.destructible_mask = pg.mask.from_surface(self.image)

    def destroy_terrain(self, location, radius):
        color = (0, 0, 0, 0)
        pg.draw.circle(self.image, color, location, radius)
        self.update_destructible_mask()

    @property
    def collision_mask(self):
        # Combine both masks for easy collision detection
        combined_mask = pg.Mask(self.size)
        combined_mask.draw(self.destructible_mask, (0, 0))
        combined_mask.draw(self.indestructible_mask, (0, 0))
        return combined_mask
