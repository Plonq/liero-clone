import random

import pygame as pg
from pygame.math import Vector2

from src import assets
from src.controllers import AiController, PlayerController
from src.engine.game import Game
from src.engine.input import (
    is_action_just_pressed,
    register_key_action,
    register_mouse_action,
)
from src.engine.utils import clamp
from src.hud import HUD
from src.worm import Worm
from src.map import Map
from src.sound import SoundEffects

WINDOW_SIZE = (1216, 800)
DISPLAY_SIZE = (608, 400)


class LieroClone(Game):
    def __init__(self):
        super().__init__(WINDOW_SIZE, DISPLAY_SIZE, "Liero Clone")
        assets.init()
        self.map = Map(self)
        self.add_object(self.map)
        self.player = Worm(self, "player", PlayerController(self))
        self.opponent = Worm(self, "opponent", AiController(self), 100, 100)
        self.add_object(self.player)
        self.add_object(self.opponent)
        self.hud = HUD(self, self.player)
        self._register_actions()
        # self.sound = SoundEffects()
        self.true_offset = [0, 0]

    def _register_actions(self):
        register_mouse_action("attack", pg.BUTTON_LEFT)
        register_mouse_action("dig", pg.BUTTON_RIGHT)
        register_key_action("spawn", pg.K_RETURN)
        register_key_action("jump", pg.K_SPACE)
        register_key_action("move_left", pg.K_a)
        register_key_action("move_right", pg.K_d)
        register_key_action("switch_weapon", pg.K_f)
        register_key_action("grapple", pg.K_e)
        register_key_action("test", pg.K_t)

    def post_update(self, dt, offset):
        self.hud.update(dt, offset)
        if is_action_just_pressed("spawn"):
            self.spawn()
        if is_action_just_pressed("test"):
            self.player.damage(20)

    def _draw(self, surface, offset):
        super()._draw(surface, offset)
        self.hud.draw(surface, offset)

    def spawn(self):
        position = Vector2(
            random.randint(self.player.width, self.display_size[0] - self.player.width),
            random.randint(
                self.player.height, self.display_size[1] - self.player.height
            ),
        )
        self.player.spawn(position)
        self.opponent.spawn(Vector2(100, 100))

    def get_visible_rect(self):
        return pg.Rect(
            self.offset.x,
            self.offset.y,
            self.display_size[0],
            self.display_size[1],
        )

    def update_offset(self, dt):
        self.true_offset[0] += (
            self.player.x
            - self.true_offset[0]
            - self.display_size[0] / 2
            + self.player.width // 2
        ) / (0.15 / dt)
        self.true_offset[1] += (
            self.player.y
            - self.true_offset[1]
            - self.display_size[1] / 2
            + self.player.height // 2
        ) / (0.15 / dt)
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

    def get_living_worms(self):
        return [worm for worm in [self.player, self.opponent] if worm.alive]

    def destroy_terrain(self, location, radius):
        self.map.destroy_terrain(location, radius)

    def get_player_position(self):
        return self.player.position


if __name__ == "__main__":
    LieroClone().run()
