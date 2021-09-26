import time

import pygame as pg
from pygame.math import Vector2

from src.assets import assets
from src.engine.font import Font
from src.engine.signals import observe
from src.engine.game import GameObject
from src.engine.utils import clamp


class HUD(GameObject):
    def __init__(self, game, worm):
        self.game = game
        self.worm = worm
        self.font = Font(assets["font"]["small"])
        self.margin = 3
        self.spacing = 3
        self.bar_max_width = 200
        self.bar_height = 4
        # Health
        self.health_bar_zero = pg.Color(201, 40, 40)
        self.health_bar_full = pg.Color(48, 201, 40)
        # Ammo/reload
        self.ammo_bar_zero = pg.Color(201, 40, 40)
        self.ammo_bar_full = pg.Color(40, 72, 201)
        # Weapon Name
        self.weapon_name = ""
        self.weapon_name_color = pg.Color("white")
        self.weapon_name_current_color = self.weapon_name_color
        self.time_of_last_weapon_switch = 0
        self.weapon_name_fade_time = 5
        # Listen to events
        observe("switched_weapon", self._on_switched_weapon)

    def _on_switched_weapon(self, previous, current, worm):
        if worm != self.worm:
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
                self.font.height * 3 + self.margin * 2 + self.spacing * 2,
            ),
        )

        # Health
        self.font.draw(
            surface,
            "health",
            pg.Color("white"),
            Vector2(self.margin * 2, self.margin * 2),
        )
        if self.worm.alive:
            rect = pg.Rect(
                self.font.calculate_width("health") + self.margin * 3,
                self.margin * 2 + self.font.height // 2 - self.bar_height // 2,
                self.bar_max_width,
                self.bar_height,
            )
            health_perc = self.worm.health / self.worm.max_health
            rect.width = self.bar_max_width * health_perc
            color = self.health_bar_zero.lerp(self.health_bar_full, health_perc)
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
        ammo_perc = (
            self.worm.current_weapon.reload_time_elapsed
            / self.worm.current_weapon.reload_time
        )
        if ammo_perc == 0:
            ammo_perc = (
                self.worm.current_weapon.rounds_left
                / self.worm.current_weapon.rounds_per_magazine
            )
        rect.width = self.bar_max_width * ammo_perc
        color = self.ammo_bar_zero.lerp(self.ammo_bar_full, ammo_perc)
        pg.draw.rect(surface, color, rect)

        # Lives
        self.font.draw(
            surface,
            f"lives: {self.worm.lives}",
            pg.Color("white"),
            Vector2(
                self.margin * 2, self.margin * 2 + (self.font.height + self.spacing) * 2
            ),
        )

        # Weapon name
        if self.weapon_name_current_color != pg.Color(0, 0, 0, 0):
            worm_pos = self.worm.position
            worm_offset = Vector2(
                self.font.calculate_width(self.weapon_name) // 2 * -1, -20
            )
            self.font.draw(
                surface,
                self.weapon_name,
                self.weapon_name_current_color,
                worm_pos + worm_offset - offset,
            )

        # Death spawn text
        if not self.worm.alive and self.worm.lives > 0:
            center_of_screen = Vector2(
                self.game.display_size[0] // 2, self.game.display_size[1] // 2
            )
            if self.worm.spawn_timer == 0:
                text = "Press Fire to spawn"
            else:
                text = "Raspawn in {:.2f}".format(self.worm.spawn_timer)
            self.font.draw_centered(
                surface,
                text,
                pg.Color("white"),
                center_of_screen,
            )
