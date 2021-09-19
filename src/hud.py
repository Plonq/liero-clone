import time

import pygame as pg
from pygame.math import Vector2

from src.assets import assets
from src.engine.font import Font
from src.engine.signals import observe
from src.engine.game import GameObject
from src.engine.utils import clamp


class HUD(GameObject):
    def __init__(self, game):
        self.game = game
        self.font = Font(assets["font"]["small"])
        self.margin = 3
        self.spacing = 3
        self.bar_max_width = 200
        self.bar_height = 4
        # Health
        self.health = 1
        self.health_bar_zero = pg.Color(201, 40, 40)
        self.health_bar_full = pg.Color(48, 201, 40)
        # Ammo/reload
        self.ammo = 0
        self.reload_perc = 0
        self.ammo_bar_zero = pg.Color(201, 40, 40)
        self.ammo_bar_full = pg.Color(40, 72, 201)
        # Weapon Name
        self.weapon_name = ""
        self.weapon_name_color = pg.Color("white")
        self.weapon_name_current_color = self.weapon_name_color
        self.time_of_last_weapon_switch = 0
        self.weapon_name_fade_time = 5
        # Listen to events
        observe("ammo", self._update_ammo)
        observe("reload_perc", self._update_reload_perc)
        observe("switched_weapon", self._on_switched_weapon)

    def _update_ammo(self, ammo_perc):
        self.ammo = ammo_perc

    def _update_reload_perc(self, reload_perc):
        self.reload_perc = reload_perc

    def _on_switched_weapon(self, previous, current):
        if current != previous:
            self.weapon_name = current.name
            # Reset color to white to display it
            self.weapon_name_current_color = pg.Color("white")
            self.time_of_last_weapon_switch = time.time()

    def update(self, dt, offset):
        if self.weapon_name_current_color != pg.Color(0, 0, 0, 0):
            perc = clamp(
                (time.time() - self.time_of_last_weapon_switch)
                / self.weapon_name_fade_time,
                0,
                1,
            )
            self.weapon_name_current_color = self.weapon_name_color.lerp(
                pg.Color(0, 0, 0, 0), perc
            )

    def draw(self, surface, offset):
        # Background
        pg.draw.rect(
            surface,
            pg.Color("black"),
            (
                self.margin,
                self.margin,
                self.bar_max_width
                + self.font.calculate_width("health")
                + self.margin * 3,
                self.font.height * 2 + self.margin * 2 + self.spacing,
            ),
        )
        # Health
        self.font.draw(
            surface,
            "health",
            pg.Color("white"),
            Vector2(self.margin * 2, self.margin * 2),
        )
        rect = pg.Rect(
            self.font.calculate_width("health") + self.margin * 3,
            self.margin * 2 + self.font.height // 2 - self.bar_height // 2,
            self.bar_max_width,
            self.bar_height,
        )
        percentage = self.health
        rect.width = self.bar_max_width * percentage
        color = self.health_bar_zero.lerp(self.health_bar_full, percentage)
        pg.draw.rect(surface, color, rect)
        # Ammo bar
        self.font.draw(
            surface,
            "ammo",
            pg.Color("white"),
            Vector2(self.margin * 2, self.margin * 2 + self.font.height + self.spacing),
        )
        rect = pg.Rect(
            self.font.calculate_width("health") + self.margin * 3,
            self.margin * 2
            + self.font.height
            + self.spacing
            + self.font.height // 2
            - self.bar_height // 2,
            self.bar_max_width,
            self.bar_height,
        )
        percentage = self.reload_perc if self.reload_perc > 0 else self.ammo
        rect.width = self.bar_max_width * percentage
        color = self.ammo_bar_zero.lerp(self.ammo_bar_full, percentage)
        pg.draw.rect(surface, color, rect)

        # Weapon name
        if self.weapon_name_current_color != pg.Color(0, 0, 0, 0):
            player_pos = self.game.get_player_position() - offset
            offset = Vector2(self.font.calculate_width(self.weapon_name) // 2 * -1, -20)
            self.font.draw(
                surface,
                self.weapon_name,
                self.weapon_name_current_color,
                player_pos + offset,
            )
