import pygame as pg

from src.assets import get_image
from src.engine.game import GameObject


class Map(GameObject):
    def __init__(self, game):
        self.game = game
        destructible = get_image("maps/default/main.png")
        indestructible = get_image("maps/default/obstacles.png")
        self.destructible = destructible
        self.indestructible = indestructible
        self.destructible_mask = pg.mask.from_surface(destructible)
        self.indestructible_mask = pg.mask.from_surface(indestructible)
        self.size = destructible.get_size()
        self.map_boundary_rects = (
            pg.Rect(-50, -50, self.size[0] + 50, 50),
            pg.Rect(-50, 0, 50, self.size[1]),
            pg.Rect(self.size[0], 0, 50, self.size[1]),
            pg.Rect(-50, self.size[1], self.size[0] + 50, 50),
        )
        self.needs_cleanup = False
        self.time_since_cleanup = 0

    def update(self, dt, offset):
        # Throttle cleanup for performance
        self.time_since_cleanup += dt
        if self.time_since_cleanup > 0.1:
            if self.needs_cleanup:
                self.clean_up()
            self.time_since_cleanup = 0

    def draw(self, surface, offset):
        adjusted_offset = (-offset.x, -offset.y)

        # Background
        surface.fill((53, 29, 15))

        # Boundary
        for map_boundary_rect in self.map_boundary_rects:
            pg.draw.rect(surface, (0, 0, 0), map_boundary_rect)

        # Destructible map - clipped to undestroyed parts
        clipping_mask = self.destructible_mask.to_surface(
            unsetcolor=(0, 0, 0, 0)
        ).convert_alpha()
        destructible_copy = self.destructible.copy()
        destructible_copy.blit(clipping_mask, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
        surface.blit(destructible_copy, adjusted_offset)

        # Indestructible map (rocks and such)
        surface.blit(self.indestructible, adjusted_offset)

    def destroy_terrain(self, location, radius):
        # Create a mask of a circle
        circle_img = pg.Surface((radius * 2, radius * 2))
        circle_img.fill((0, 0, 0))
        circle_img.set_colorkey((0, 0, 0))
        pg.draw.circle(circle_img, (255, 255, 255), (radius, radius), radius)
        circle_mask = pg.mask.from_surface(circle_img)
        # Erase circular area of destructible mask
        self.destructible_mask.erase(
            circle_mask, (int(location.x - radius), int(location.y - radius))
        )
        self.needs_cleanup = True

    def clean_up(self):
        """Remove areas of destructible that are smaller than 20 pixels."""
        new_mask = pg.Mask(self.size)
        for mask in self.destructible_mask.connected_components(20):
            new_mask.draw(mask, (0, 0))
        self.destructible_mask = new_mask
        self.needs_cleanup = False

    @property
    def collision_mask(self):
        """Return combination of destructible and indestructible masks."""
        combined_mask = pg.Mask(self.size)
        combined_mask.draw(self.destructible_mask, (0, 0))
        combined_mask.draw(self.indestructible_mask, (0, 0))
        return combined_mask
