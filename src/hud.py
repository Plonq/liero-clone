import random
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
        self.z_index = 1000
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
        observe("worm_damaged", self._worm_damaged)

    def _on_switched_weapon(self, previous, current, worm):
        if worm == self.worm:
            if current != previous:
                self.weapon_name = current.name
                # Reset color to white to display it
                self.weapon_name_current_color = pg.Color("white")
                self.time_of_last_weapon_switch = time.time()

    def _worm_damaged(self, dmg, worm):
        self.game.add_object(
            DamageIndicator(
                self.game, self.font, position=worm.position - Vector2(0, 10), value=dmg
            )
        )

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
        self._draw_player_stats(surface, offset)
        self._draw_targeted_overlay(surface, offset)
        self._draw_minimap(surface, offset)

    def _draw_player_stats(self, surface, offset):
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
            "Health",
            pg.Color("white"),
            Vector2(self.margin * 2, self.margin * 2),
        )
        if self.worm.alive:
            rect = pg.Rect(
                self.font.calculate_width("Health") + self.margin * 3,
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
            "Ammo",
            pg.Color("white"),
            Vector2(self.margin * 2, self.margin * 2 + self.font.height + self.spacing),
        )
        rect = pg.Rect(
            self.font.calculate_width("Health") + self.margin * 3,
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
        lives_text = f"Lives: {self.worm.lives}"
        self.font.draw(
            surface,
            lives_text,
            pg.Color(255, 70, 70),
            Vector2(
                self.margin * 2, self.margin * 2 + (self.font.height + self.spacing) * 2
            ),
        )

        # Kills
        self.font.draw(
            surface,
            f"Kills: {self.worm.kills}",
            pg.Color(80, 230, 100),
            Vector2(
                self.margin * 5 + self.font.calculate_width(lives_text),
                self.margin * 2 + (self.font.height + self.spacing) * 2,
            ),
        )

    def _draw_targeted_overlay(self, surface, offset):
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

    def _draw_minimap(self, surface, offset):
        minimap = self.game.get_minimap()
        minimap_size = minimap.get_size()
        scale = minimap_size[0] / self.game.map.size[0]
        for worm in self.game.get_living_worms():
            pg.draw.circle(minimap, worm.color, worm.position * scale, 1)
        x = self.game.display_size[0] - minimap_size[0] - 5
        y = 5
        surface.blit(minimap, (x, y))
        pg.draw.rect(
            surface,
            pg.Color("white"),
            (x - 1, y - 1, minimap_size[0] + 2, minimap_size[1] + 2),
            width=1,
        )


class DamageIndicator(GameObject):
    def __init__(self, game, font, position, value=0):
        self.game = game
        self.z_index = 1000
        self.font = font
        self.position = position + Vector2(
            random.randint(-10, 10), random.randint(-10, 10)
        )
        self.value = value
        self.lifespan = 1
        self.age = 0
        self.color = pg.Color("white")

    def update(self, dt, offset):
        self.age += dt
        if self.age >= self.lifespan:
            self.game.remove_object(self)
            return
        self.position -= Vector2(0, 1)
        alpha = (1 - self.age / self.lifespan) * 255
        self.color.a = int(alpha)

    def draw(self, surface, offset):
        self.font.draw_centered(
            surface, str(self.value), self.color, self.position - offset
        )
