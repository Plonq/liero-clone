import pygame as pg

from src.engine.signals import observe
from src.engine.game import GameObject


class HUD(GameObject):
    def __init__(self, game):
        self.game = game
        self.bar_max_width = 150
        self.ammo = 0
        self.reload_perc = 0
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
        rect = pg.Rect(10, 10, self.bar_max_width, 5)
        if self.reload_perc > 0:
            rect.width = self.bar_max_width * self.reload_perc
        else:
            rect.width = self.bar_max_width * self.ammo
        pg.draw.rect(surface, (255, 255, 255), rect)
