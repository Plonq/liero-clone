import random

import pygame as pg
from pygame.math import Vector2

from src.assets import assets
from src.engine.game import GameObject
from src.engine.gfx import Effect
from src.engine.utils import blit_centered
from src.mixins import ParticleCollisionMixin


class SmallExplosion(Effect):
    def __init__(self, game, position):
        super().__init__(
            game,
            position=position,
            sprite_strip=assets["img"]["explosions"]["small"],
            lifespan=0.3,
        )


class BloodParticle(ParticleCollisionMixin, GameObject):
    big_img = pg.Surface((2, 2))
    small_img = pg.Surface((1, 1))

    def __init__(self, game, position, velocity, drip=False):
        self.game = game
        self.image = (
            self.big_img.copy().convert_alpha()
            if drip
            else self.small_img.copy().convert_alpha()
        )
        self.color = pg.Color(165, 10, 28, random.randint(120, 250))
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
