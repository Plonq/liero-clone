import random
import time

import pygame as pg
from pygame.math import Vector2

from src.assets import assets
from src.engine.game import GameObject
from src.engine.gfx import Effect
from src.engine.signals import emit_event
from src.engine.utils import blit_centered, create_circle_mask
from src.mixins import ParticleCollisionMixin, WormCollisionMixin


class Explosion(WormCollisionMixin, Effect):
    explosion_sizes = {"small": 7, "medium": 12, "large": 16}

    def __init__(self, game, position, size, damage, worm, aoe=False, multi=False):
        self.radius = self.explosion_sizes[size]
        super().__init__(
            game,
            position=position,
            sprite_strip=assets["img"]["explosions"][size],
            lifespan=0.042 * self.radius,
        )
        self.z_index = random.randint(20, 120)
        self.size = size
        self.mask = create_circle_mask(self.radius)
        self.damage = damage
        self.aoe = aoe
        self.worm = worm
        self.multi = multi
        self.time_of_explode = time.time()
        self.time_since_last_multi = 0
        self._explode()
        emit_event("small_explosion", position=position)

    def _explode(self):
        self.game.destroy_terrain(self.position, self.explosion_sizes[self.size])
        for worm in self.game.get_living_worms():
            if self.aoe:
                self._do_damage(worm, worm.position, dist_offset=10)
            else:
                collision = self.collided_with_worm(self.position, worm, self.mask)
                if collision:
                    self._do_damage(worm, collision)
        self.game.set_screen_flash(self.radius * 2)
        self.game.set_screen_shake(self.radius ** 2 // 15)

    def _do_damage(self, worm, impact_position, dist_offset=0):
        dist = self.position.distance_to(impact_position) - dist_offset
        dmg = min(self.damage - int(self.damage * (dist / self.radius)), self.damage)
        if dmg > 0:
            worm.damage(dmg, attacker=self.worm)

    def update(self, dt, offset):
        super().update(dt, offset)
        if self.multi:
            self.time_since_last_multi += dt
            if time.time() - self.time_of_explode < 0.2:
                if self.time_since_last_multi > random.randint(0, 1) / 100:
                    pos = Vector2(self.position) + Vector2(
                        random.randint(
                            -self.radius,
                            self.radius,
                        ),
                        random.randint(
                            -self.radius,
                            self.radius,
                        ),
                    )
                    self.game.add_object(
                        Explosion(self.game, pos, "small", self.damage // 3, self.worm)
                    )


class BloodParticle(ParticleCollisionMixin, GameObject):
    big_img = pg.Surface((2, 2))
    small_img = pg.Surface((1, 1))

    def __init__(self, game, position, velocity, drip=False):
        self.game = game
        self.z_index = 60
        self.image = (
            self.big_img.copy().convert_alpha()
            if drip
            else self.small_img.copy().convert_alpha()
        )
        color = pg.Color(0, 0, 0)
        color.hsva = (353, 94, random.randint(60, 70), random.randint(45, 95))
        self.color = color
        self.image.fill(self.color)
        self.mask = pg.Mask((1, 1), fill=True)
        self.position = position
        self.velocity = velocity * random.randint(80, 120) / 80
        self.drip = drip
        self.time_since_last_drip = 0

    def update(self, dt, offset):
        self.velocity.y += 2 if self.drip else 1.5
        self.position += self.velocity * dt
        if self.drip:
            self.time_since_last_drip += dt
            if self.time_since_last_drip > random.randint(10, 30) / 100:
                self.game.add_object(
                    BloodParticle(
                        self.game, Vector2(self.position), Vector2(self.velocity / 5)
                    )
                )
                self.time_since_last_drip = 0
        if self.collided_with_map(self.position, self.mask, self.game):
            image = pg.Surface((1, 1))
            image.fill(pg.Color(self.color.r, self.color.g, self.color.b))
            self.game.stain_map(self.position, image)
            self.game.remove_object(self)

    def draw(self, surface, offset):
        blit_centered(self.image, surface, self.position - offset)
