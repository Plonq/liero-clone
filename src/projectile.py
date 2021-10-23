import math
import random

import pygame as pg
from pygame.math import Vector2

from src.assets import assets, get_image
from src.engine.game import GameObject
from src.engine.utils import blit_centered, rad_to_deg
from src.gfx import Explosion
from src.mixins import ParticleCollisionMixin, WormCollisionMixin


class Projectile(ParticleCollisionMixin, WormCollisionMixin, GameObject):
    def __init__(self, game, worm, img, start_pos, velocity, damage):
        self.game = game
        self.worm = worm
        self.image = img
        self.mask = pg.Mask((1, 1), True)
        self.position = start_pos
        self.velocity = velocity
        self.damage = damage

    def _move_and_collide(self, dt):
        movement = self.velocity * dt
        new_position = self.position + movement
        collision = self.collided_with_map(
            new_position, self.mask, self.game, previous_position=self.position
        )
        if collision:
            self.position = Vector2(collision)
            return {"type": "map"}
        for worm in self.game.get_living_worms():
            collision = self.collided_with_worm(
                self.position, worm, self.mask, previous_position=self.position
            )
            if collision:
                self.position = Vector2(collision)
                return {"type": "worm", "worm": worm}
        self.position = new_position
        return {"type": None}

    def explode(self):
        self.game.remove_object(self)
        self.game.add_object(
            Explosion(self.game, self.position, "small", self.damage, self.worm)
        )

    def draw(self, surface, offset):
        blit_centered(self.image, surface, self.position - offset)


class Bullet(Projectile):
    def __init__(self, game, worm, start_pos, velocity, damage):
        img = assets["img"]["projectiles"]["bullet"]
        super().__init__(game, worm, img, start_pos, velocity, damage)

    def update(self, dt, offset):
        collision = self._move_and_collide(dt)
        if collision["type"] is not None:
            self.explode()
            self.game.remove_object(self)


class Rocket(Projectile):
    def __init__(self, game, worm, start_pos, velocity, damage):
        rotated_img = pg.transform.rotate(
            assets["img"]["projectiles"]["missile"],
            -rad_to_deg(math.atan2(velocity.y, velocity.x)),
        )
        super().__init__(
            game,
            worm,
            rotated_img,
            start_pos,
            velocity,
            damage,
        )
        self.mask = pg.Mask((5, 5), True)
        self.time_since_last_puff = 0

    def update(self, dt, offset):
        self.time_since_last_puff += dt
        if self.time_since_last_puff > 0.03:
            self._emit_puff()
            self.time_since_last_puff = 0
        collision = self._move_and_collide(dt)
        if collision["type"]:
            self.explode()

    def _emit_puff(self):
        self.game.add_object(
            FadingImage(self.game, assets["img"]["smoke"], self.position, 2)
        )

    def explode(self):
        self.game.add_object(
            Explosion(
                self.game, self.position, "large", self.damage, self.worm, multi=True
            )
        )
        self.game.remove_object(self)


class FadingImage(GameObject):
    def __init__(self, game, img, position, lifespan, drift=100):
        self.game = game
        self.orig_img = img
        self.img = None
        self.position = Vector2(position)
        self.lifespan = lifespan
        self.time_since_born = 0
        self.velocity = Vector2(
            random.randint(-drift, drift) / 500, random.randint(-drift, drift) / 500
        )

    def update(self, dt, offset):
        self.position += self.velocity
        alpha = 255 - self.time_since_born / self.lifespan * 255
        if alpha <= 20:
            self.game.remove_object(self)
        else:
            scale = (
                (self.time_since_born + 1) / self.lifespan * self.orig_img.get_width()
            )
            self.img = pg.transform.scale(
                self.orig_img.copy(),
                (int(scale), int(scale)),
            )
            self.img.fill(
                (255, 255, 255, alpha), None, special_flags=pg.BLEND_RGBA_MULT
            )
            self.time_since_born += dt

    def draw(self, surface, offset):
        if self.img:
            blit_centered(self.img, surface, self.position - offset)
