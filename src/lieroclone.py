import pygame as pg

from src.assets import Assets
from src.engine.game import Game
from src.input import Input
from src.world import World

clock = pg.time.Clock()

WINDOW_SIZE = (1216, 800)
DISPLAY_SIZE = (608, 400)


class LieroClone(Game):
    def __init__(self):
        super().__init__(WINDOW_SIZE, DISPLAY_SIZE, "Liero Clone")
        self.assets = Assets()
        self.world = World(self)
        self.add_object(self.world)
        self.states = {
            "spawn": False,
            "jump": False,
            "move_left": False,
            "move_right": False,
            "dig": False,
            "attack": False,
            "switch_weapon": False,
        }

    def _process_events(self):
        self._reset_transient_states()
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == pg.BUTTON_LEFT:
                    self.states["attack"] = True
                if event.button == pg.BUTTON_RIGHT:
                    self.states["dig"] = True

            if event.type == pg.MOUSEBUTTONUP:
                if event.button == pg.BUTTON_LEFT:
                    self.states["attack"] = False

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    self.states["spawn"] = True
                if event.key == pg.K_SPACE:
                    self.states["jump"] = True
                if event.key == pg.K_a:
                    self.states["move_left"] = True
                if event.key == pg.K_d:
                    self.states["move_right"] = True
                if event.key == pg.K_e:
                    self.states["switch_weapon"] = True

            if event.type == pg.KEYUP:
                if event.key == pg.K_a:
                    self.states["move_left"] = False
                if event.key == pg.K_d:
                    self.states["move_right"] = False

            if event.type == pg.QUIT:
                self.quit()

    def _reset_transient_states(self):
        self.states["jump"] = False
        self.states["dig"] = False
        self.states["spawn"] = False
        self.states["switch_weapon"] = False


if __name__ == "__main__":
    LieroClone().run()
