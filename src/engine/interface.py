import pygame as pg
from pygame.math import Vector2

from src.assets import assets
from src.engine.font import Font
from src.engine.game import GameObject
from src.engine.input import is_action_just_pressed


class MenuItem:
    def __init__(self, text_fn, activate_fn):
        self.text_fn = text_fn
        self.activate_fn = activate_fn
        self.color = pg.Color("white")
        self.selected_color = pg.Color("red")
        self.font = Font(assets["font"]["large"])

    def update(self, dt):
        pass

    def draw(self, surface, position, selected=False):
        self.font.draw_centered(
            surface,
            self.text_fn(),
            pg.Color("black"),
            Vector2(position.x + 1, position.y + 1),
        )
        self.font.draw_centered(
            surface,
            self.text_fn(),
            self.selected_color if selected else self.color,
            position,
        )

    def activate(self):
        self.activate_fn()


class Menu(GameObject):
    def __init__(self, game, options, position):
        self.game = game
        self.position = position
        self.font = Font(assets["font"]["large"])
        self.position = position
        self.spacing = 10
        self.items = self._build_items(options)
        self.selected_item = self.items[0]

    def _build_items(self, options):
        self.start_y = (
            self.position.y - (len(options) * (self.font.height + self.spacing)) // 2
        )
        return [
            MenuItem(text_fn=option["text"], activate_fn=option["execute"])
            for option in options
        ]

    def update(self, dt, offset):
        if is_action_just_pressed("down"):
            try:
                self.selected_item = self.items[
                    self.items.index(self.selected_item) + 1
                ]
            except IndexError:
                self.selected_item = self.items[0]
        elif is_action_just_pressed("up"):
            try:
                self.selected_item = self.items[
                    self.items.index(self.selected_item) - 1
                ]
            except IndexError:
                self.selected_item = self.items[len(self.items) - 1]

        elif is_action_just_pressed("select"):
            self.selected_item.activate()

    def draw(self, surface, offset):
        pos = Vector2(self.position.x, self.start_y)
        for item in self.items:
            item.draw(surface, pos, selected=item == self.selected_item)
            pos.y += self.font.height + self.spacing
