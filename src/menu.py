import pygame as pg
from pygame.math import Vector2

from src.assets import assets
from src.engine.font import Font
from src.engine.game import GameObject
from src.engine.input import is_action_just_pressed


class Menu(GameObject):
    def __init__(self, game):
        self.game = game
        self.bg = pg.Surface(self.game.display_size)
        self.bg.fill((150, 150, 150))
        self.started = False
        self.options = [
            {
                "name": "start",
                "text": lambda: "Resume" if self.started else "Start",
                "execute": lambda: self.start(),
            },
            {
                "name": "fullscreen",
                "text": lambda: "Toggle Fullscreen",
                "execute": lambda: self.game.toggle_fullscreen(),
            },
            {
                "name": "quit",
                "text": lambda: "Quit",
                "execute": lambda: self.game.quit(),
            },
        ]
        self.option_names = [option["name"] for option in self.options]
        self.selected_option = "start"
        self.center_of_screen = Vector2(
            self.game.display_size[0] // 2, self.game.display_size[1] // 2
        )
        self.font = Font(assets["font"]["large"])
        self.spacing = 10
        self.start_y = (
            self.center_of_screen.y
            - (len(self.options) * (self.font.height + self.spacing)) // 2
        )

    def update(self, dt, offset):
        if is_action_just_pressed("down"):
            try:
                self.selected_option = self.option_names[
                    self.option_names.index(self.selected_option) + 1
                ]
            except IndexError:
                self.selected_option = self.option_names[0]
        elif is_action_just_pressed("up"):
            try:
                self.selected_option = self.option_names[
                    self.option_names.index(self.selected_option) - 1
                ]
            except IndexError:
                self.selected_option = self.option_names[len(self.option_names) - 1]

        elif is_action_just_pressed("select"):
            for option in self.options:
                if option["name"] == self.selected_option:
                    option["execute"]()
                    break

    def draw(self, surface, offset):
        surface.blit(self.bg, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
        pos = Vector2(self.center_of_screen.x, self.start_y)
        for option in self.options:
            self.font.draw_centered(
                surface,
                option["text"](),
                pg.Color("black"),
                Vector2(pos.x + 1, pos.y + 1),
            )
            color = (
                pg.Color("red")
                if option["name"] == self.selected_option
                else pg.Color("white")
            )
            self.font.draw_centered(
                surface,
                option["text"](),
                color,
                pos,
            )
            pos.y += self.font.height + self.spacing

    def start(self):
        self.started = True
        self.game.set_state("playing")
