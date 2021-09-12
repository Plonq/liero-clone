import random

import pygame as pg
from pygame.math import Vector2

from src import assets
from src.engine.game import Game
from src.engine.input import (
    is_action_just_pressed,
    register_key_action,
    register_mouse_action,
)
from src.engine.utils import clamp
from src.player import Player
from src.map import Map

WINDOW_SIZE = (1216, 800)
DISPLAY_SIZE = (608, 400)


class LieroClone(Game):
    def __init__(self):
        super().__init__(WINDOW_SIZE, DISPLAY_SIZE, "Liero Clone")
        assets.init()
        self.map = Map(self)
        self.player = Player(self)
        self.add_object(self.map)
        self._register_actions()
        self.true_offset = [0, 0]

    def post_update(self, dt):
        if is_action_just_pressed("spawn"):
            self.spawn()
        if self.player.alive:
            self.player.move(self.get_collision_rects(), self.get_collision_mask(), dt)

    def spawn(self):
        position = Vector2(
            random.randint(self.player.width, self.display_size[0] - self.player.width),
            random.randint(
                self.player.height, self.display_size[1] - self.player.height
            ),
        )
        self.map.destroy_terrain(position, radius=self.player.height * 0.8)
        self.player.x, self.player.y = position
        self.player.alive = True
        self.add_object(self.player)

    def get_visible_rect(self):
        return pg.Rect(
            self.offset.x,
            self.offset.y,
            self.display_size[0],
            self.display_size[1],
        )

    def update_offset(self):
        self.true_offset[0] += (
            self.player.x
            - self.true_offset[0]
            - self.display_size[0] / 2
            + self.player.width // 2
        ) / 15
        self.true_offset[1] += (
            self.player.y
            - self.true_offset[1]
            - self.display_size[1] / 2
            + self.player.height // 2
        ) / 15
        # Clamp to prevent camera going outside map
        self.true_offset[0] = clamp(
            self.true_offset[0], 0, self.map.size[0] - self.display_size[0]
        )
        self.true_offset[1] = clamp(
            self.true_offset[1], 0, self.map.size[1] - self.display_size[1]
        )
        self.offset = Vector2(int(self.true_offset[0]), int(self.true_offset[1]))

    def is_within_map(self, position):
        return pg.Rect(0, 0, *self.map.size).collidepoint(position.x, position.y)

    def get_collision_rects(self):
        return self.map.map_boundary_rects

    def get_collision_mask(self):
        return self.map.collision_mask

    def destroy_terrain(self, location, radius):
        self.map.destroy_terrain(location, radius)

    def _register_actions(self):
        register_mouse_action("attack", pg.BUTTON_LEFT)
        register_mouse_action("dig", pg.BUTTON_RIGHT)
        register_key_action("spawn", pg.K_RETURN)
        register_key_action("jump", pg.K_SPACE)
        register_key_action("move_left", pg.K_a)
        register_key_action("move_right", pg.K_d)
        register_key_action("switch_weapon", pg.K_e)
        register_key_action("test", pg.K_t)


if __name__ == "__main__":
    LieroClone().run()
