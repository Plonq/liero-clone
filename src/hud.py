import pygame as pg

from src.engine.signals import observe
from src.engine.game import GameObject


class HUD(GameObject):
    def __init__(self, game):
        self.game = game
        self.bar_max_width = 200
        self.bar_height = 4
        self.ammo = 0
        self.reload_perc = 0
        self.ammo_bar_zero = pg.Color(201, 40, 40)
        self.ammo_bar_full = pg.Color(40, 72, 201)
        observe("ammo", self._update_ammo)
        observe("reload_perc", self._update_reload_perc)

    def _update_ammo(self, ammo_perc):
        self.ammo = ammo_perc

    def _update_reload_perc(self, reload_perc):
        self.reload_perc = reload_perc

    def update(self, dt, offset):
        pass

    def draw(self, surface, offset):
        # Ammo bar
        rect = pg.Rect(10, 10, self.bar_max_width, self.bar_height)
        percentage = self.reload_perc if self.reload_perc > 0 else self.ammo
        rect.width = self.bar_max_width * percentage
        color = self.ammo_bar_zero.lerp(self.ammo_bar_full, percentage)
        pg.draw.rect(surface, color, rect)
