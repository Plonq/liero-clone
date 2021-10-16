import pygame as pg
from pygame.math import Vector2

from src.assets import assets
from src.engine.font import Font
from src.engine.game import GameObject
from src.engine.input import (
    is_action_just_pressed,
    register_mouse_action,
    register_mouse_move_hook,
)


class MenuItem:
    def __init__(self, game, position, text_fn, activate_fn):
        self.game = game
        self.position = position
        self.text_fn = text_fn
        self.activate_fn = activate_fn
        self.color = pg.Color("white")
        self.selected_color = pg.Color("red")
        self.font = Font(assets["font"]["large"])

    def update(self, dt):
        if is_action_just_pressed("menu_click"):
            if self.is_intersecting(self.game.get_mouse_pos()):
                self.activate_fn()

    def draw(self, surface, selected=False):
        self.font.draw_centered(
            surface,
            self.text_fn(),
            pg.Color("black"),
            Vector2(self.position.x + 1, self.position.y + 1),
        )
        self.font.draw_centered(
            surface,
            self.text_fn(),
            self.selected_color if selected else self.color,
            self.position,
        )

    def activate(self):
        self.activate_fn()

    def is_intersecting(self, point):
        size = self.get_size()
        rect = pg.Rect((0, 0), size)
        rect.center = self.position
        if rect.collidepoint(point.x, point.y):
            return True
        return False

    def get_size(self):
        return self.font.calculate_width(self.text_fn()), self.font.height


class Menu(GameObject):
    def __init__(self, game, options, position):
        self.game = game
        self.position = position
        self.font = Font(assets["font"]["large"])
        self.position = position
        self.spacing = 10
        self.items = self._build_items(options)
        self.selected_item = self.items[0]
        register_mouse_move_hook(self._on_mouse_move)

    def _build_items(self, options):
        self.start_y = (
            self.position.y - (len(options) * (self.font.height + self.spacing)) // 2
        )
        item_pos = Vector2(self.position.x, self.start_y)
        items = []
        for option in options:
            items.append(
                MenuItem(
                    self.game,
                    Vector2(item_pos),
                    text_fn=option["text"],
                    activate_fn=option["execute"],
                )
            )
            item_pos.y += self.font.height + self.spacing
        return items

    def _on_mouse_move(self, pos, rel):
        item_pos = Vector2(self.position.x, self.start_y)
        for item in self.items:
            size = item.get_size()
            rect = pg.Rect((0, 0), size)
            rect.center = item_pos
            mouse_pos = self.game.get_mouse_pos()
            if rect.collidepoint(*mouse_pos):
                self.selected_item = item
                break
            item_pos.y += self.font.height + self.spacing

    def update(self, dt, offset):
        for item in self.items:
            item.update(dt)
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

    def set_selected_item(self, item):
        self.selected_item = item

    def draw(self, surface, offset):
        for item in self.items:
            item.draw(surface, selected=item == self.selected_item)
