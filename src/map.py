import pygame as pg

from src.assets import get_asset
from src.engine.game import GameObject
from src.engine.input import is_action_pressed


class Map(GameObject):
    def __init__(self, game):
        self.game = game
        destructible, indestructible = get_asset("maps", "default")
        self.destructible = destructible
        self.indestructible = indestructible
        self.destructible_mask = pg.mask.from_surface(destructible)
        self.indestructible_mask = pg.mask.from_surface(indestructible)
        self.size = destructible.get_size()
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
        adjusted_offset = (-offset.x, -offset.y)
        surface.blit(self.destructible, adjusted_offset)
        surface.blit(self.indestructible, adjusted_offset)

        if is_action_pressed("test"):
            surface.blit(self.destructible_mask.to_surface(), adjusted_offset)

    def destroy_terrain(self, location, radius):
        # Destroy part of image
        color = (0, 0, 0, 0)
        radius = int(round(radius))
        pg.draw.circle(self.destructible, color, location, radius)
        # Destroy part of mask (instead of just doing pg.mask.from_surface again
        # on the whole image which is very slow)
        circle_img = pg.Surface((radius * 2, radius * 2))
        circle_img.fill((0, 0, 0))
        circle_img.set_colorkey((0, 0, 0))
        pg.draw.circle(circle_img, (255, 255, 255), (radius, radius), radius)
        circle_mask = pg.mask.from_surface(circle_img)
        self.destructible_mask.erase(
            circle_mask, (int(location.x - radius), int(location.y - radius))
        )

    @property
    def collision_mask(self):
        # Combine both masks for easy collision detection
        combined_mask = pg.Mask(self.size)
        combined_mask.draw(self.destructible_mask, (0, 0))
        combined_mask.draw(self.indestructible_mask, (0, 0))
        return combined_mask
