import pygame as pg

from src.assets import Assets
from src.engine.game import Game
from src.engine.input import register_key_action, register_mouse_action
from src.world import World

WINDOW_SIZE = (1216, 800)
DISPLAY_SIZE = (608, 400)


class LieroClone(Game):
    def __init__(self):
        super().__init__(WINDOW_SIZE, DISPLAY_SIZE, "Liero Clone")
        self.assets = Assets()
        self.world = World(self)
        self.add_object(self.world)
        self._register_actions()

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
