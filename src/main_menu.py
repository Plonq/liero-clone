import pygame as pg
from pygame.math import Vector2

from src.engine.game import GameObject
from src.engine.interface import Menu


class MainMenu(GameObject):
    def __init__(self, game):
        self.game = game
        self.bg = pg.Surface(self.game.display_size)
        self.bg.fill((150, 150, 150))
        self.started = False
        options = [
            {
                "text": lambda: "Resume" if self.started else "Single Player",
                "execute": lambda: self.start(multi=False),
            },
            # {
            #     "text": lambda: "Resume" if self.started else "Multiplayer",
            #     "execute": lambda: self.start(multi=True),
            # },
            {
                "text": lambda: "Toggle Fullscreen",
                "execute": lambda: self.game.toggle_fullscreen(),
            },
            {
                "text": lambda: "Quit",
                "execute": lambda: self.game.quit(),
            },
        ]
        center_of_screen = Vector2(
            self.game.display_size[0] // 2, self.game.display_size[1] // 2
        )
        self.menu = Menu(game, options, center_of_screen)

    def update(self, dt, offset):
        self.menu.update(dt, offset)

    def draw(self, surface, offset):
        surface.blit(self.bg, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
        self.menu.draw(surface, offset)

    def start(self, multi=False):
        self.started = True
        self.game.start_game(multi)
