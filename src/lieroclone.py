import random

import pygame as pg
from pygame.math import Vector2

from src.assets import Assets
from src.engine.game import Game
from src.engine.input import (
    is_action_pressed,
    register_key_action,
    register_mouse_action,
)
from src.engine.utils import clamp
from src.player import Player
from src.world import World

WINDOW_SIZE = (1216, 800)
DISPLAY_SIZE = (608, 400)


class LieroClone(Game):
    def __init__(self):
        super().__init__(WINDOW_SIZE, DISPLAY_SIZE, "Liero Clone")
        self.assets = Assets()
        self.world = World(self)
        self.player = Player(self)
        self.add_object(self.world)
        self.add_object(self.player)
        self._register_actions()
        self.true_offset = [0, 0]

    def pre_update(self, dt):
        pass

    def post_update(self, dt):
        if is_action_pressed("spawn"):
            if not self.player.alive:
                self.spawn()
        self.player.move(self.world.map_boundary_rects, self.world.mask, dt)

    def spawn(self):
        position = Vector2(
            random.randint(self.player.width, self.display_size[0] - self.player.width),
            random.randint(
                self.player.height, self.display_size[1] - self.player.height
            ),
        )
        self.world.destroy_terrain(position, radius=self.player.height * 0.8)
        self.player.x, self.player.y = position
        self.player.alive = True

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
            self.true_offset[0], 0, self.world.size[0] - self.display_size[0]
        )
        self.true_offset[1] = clamp(
            self.true_offset[1], 0, self.world.size[1] - self.display_size[1]
        )
        self.offset = Vector2(int(self.true_offset[0]), int(self.true_offset[1]))

    def _register_actions(self):
        register_mouse_action("attack", pg.BUTTON_LEFT)
        register_mouse_action("dig", pg.BUTTON_RIGHT)
        register_key_action("spawn", pg.K_RETURN)
        register_key_action("jump", pg.K_SPACE)
        register_key_action("move_left", pg.K_a)
        register_key_action("move_right", pg.K_d)
        register_key_action("switch_weapon", pg.K_e)


if __name__ == "__main__":
    LieroClone().run()
