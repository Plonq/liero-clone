import random

import pygame as pg
from pygame.math import Vector2

from src.assets import get_image
from src.engine.game import GameObject
from src.engine.signals import observe
from src.engine.utils import blit_centered


class Map(GameObject):
    def __init__(self, game, size=(1024, 1024)):
        self.game = game
        self.z_index = 50
        self.size = size
        self._build_map()
        self.needs_cleanup = False
        self.time_since_cleanup = 0
        self.map_boundary_rects = (
            pg.Rect(-50, -50, self.size[0] + 50, 50),
            pg.Rect(-50, 0, 50, self.size[1]),
            pg.Rect(self.size[0], 0, 50, self.size[1]),
            pg.Rect(-50, self.size[1], self.size[0] + 50, 50),
        )

    def _build_map(self):
        dirt_tile = get_image("maps/default/dirt.png").convert()
        bg_tile = get_image("maps/default/bg.png").convert()
        detail12 = get_image("maps/default/obstacles/detail-12x12.png").convert_alpha()
        rock16 = get_image("maps/default/obstacles/rock-16x16.png").convert_alpha()
        rock32 = get_image("maps/default/obstacles/rock-32x32.png").convert_alpha()
        rock64 = get_image("maps/default/obstacles/rock-64x48.png").convert_alpha()

        tile_size = dirt_tile.get_size()

        dirt_img = pg.Surface(self.size).convert_alpha()
        bg_img = pg.Surface(self.size).convert_alpha()
        obstacle_img = pg.Surface(self.size).convert_alpha()

        for y in range(self.size[1] // tile_size[1]):
            for x in range(self.size[0] // tile_size[0]):
                location = (x * tile_size[0], y * tile_size[1])

                # Destructible
                bg_img.blit(bg_tile, location)
                dirt_img.blit(dirt_tile, location)
                if random.randint(1, 8) == 5:
                    offset = random.randint(
                        0, tile_size[0] - detail12.get_width()
                    ), random.randint(0, tile_size[1] - detail12.get_height())
                    dirt_img.blit(
                        detail12, (location[0] + offset[0], location[1] + offset[1])
                    )

                # Indestructible
                if random.randint(1, 10) == 5:
                    offset = random.randint(
                        0, tile_size[0] - rock32.get_width()
                    ), random.randint(0, tile_size[1] - rock32.get_height())
                    obstacle_img.blit(
                        rock32, (location[0] + offset[0], location[1] + offset[1])
                    )
                elif random.randint(1, 10) == 5:
                    offset = random.randint(
                        0, tile_size[0] - rock64.get_width()
                    ), random.randint(0, tile_size[1] - rock64.get_height())
                    obstacle_img.blit(
                        rock64, (location[0] + offset[0], location[1] + offset[1])
                    )
                elif random.randint(1, 10) == 5:
                    offset = random.randint(
                        0, tile_size[0] - rock16.get_width()
                    ), random.randint(0, tile_size[1] - rock16.get_height())
                    obstacle_img.blit(
                        rock16, (location[0] + offset[0], location[1] + offset[1])
                    )

        dirt_img.blit(obstacle_img, (0, 0))

        self.bg = Background(bg_img)
        self.game.add_object(self.bg)
        self.shadow = Shadow(self.size)
        self.game.add_object(self.shadow)

        self.destructible = dirt_img
        self.destructible_mask = pg.Mask(self.size, fill=True)
        self.indestructible_mask = pg.mask.from_surface(obstacle_img)

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

        clipping_mask = self.destructible_mask.to_surface(
            unsetcolor=(0, 0, 0, 0)
        ).convert_alpha()

        self.shadow.draw_shadow_with_clipping_mask(clipping_mask, Vector2(0))

        # Destructible map
        destructible_copy = self.destructible.copy()
        destructible_copy.blit(clipping_mask, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
        surface.blit(destructible_copy, adjusted_offset)

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
        self.destructible_mask.draw(self.indestructible_mask, (0, 0))
        self.needs_cleanup = True

    def stain_map(self, position, image):
        self.destructible.blit(image, position)

    def clean_up(self):
        """Remove areas of destructible that are smaller than 20 pixels."""
        new_mask = pg.Mask(self.size)
        for mask in self.destructible_mask.connected_components(20):
            new_mask.draw(mask, (0, 0))
        self.destructible_mask = new_mask
        self.needs_cleanup = False

    def get_collision_mask(self):
        """Return combination of destructible and indestructible masks."""
        combined_mask = pg.Mask(self.size)
        combined_mask.draw(self.destructible_mask, (0, 0))
        combined_mask.draw(self.indestructible_mask, (0, 0))
        return combined_mask

    def get_collision_masks(self):
        """Return masks used for collision as list."""
        return [self.destructible_mask, self.indestructible_mask]


class Background(GameObject):
    def __init__(self, img):
        self.z_index = 0
        self.img = img

    def draw(self, surface, offset):
        surface.blit(self.img, offset * -1)


class Shadow(GameObject):
    def __init__(self, size):
        self.z_index = 10
        self.shadow_img = pg.Surface(size)
        self.reset()
        observe("cast_shadow", self.draw_shadow)

    def reset(self):
        self.shadow_img.fill(pg.Color("white"))

    def draw_shadow(self, mask, position, centered=False):
        clipping_mask = mask.to_surface(unsetcolor=(0, 0, 0, 0)).convert_alpha()
        self.draw_shadow_with_clipping_mask(clipping_mask, position, centered)

    def draw_shadow_with_clipping_mask(self, clipping_mask, position, centered=False):

        shadow = pg.Surface(clipping_mask.get_size()).convert_alpha()
        shadow.fill((200, 200, 220))
        shadow.blit(clipping_mask, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
        if centered:
            blit_centered(shadow, self.shadow_img, position)
        else:
            self.shadow_img.blit(shadow, position)

    def draw(self, surface, offset: Vector2):
        surface.blit(
            self.shadow_img,
            offset * -1 + Vector2(-3, 3),
            special_flags=pg.BLEND_RGBA_MULT,
        )
        self.reset()
