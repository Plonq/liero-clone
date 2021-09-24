import pygame as pg
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
    image = pg.Surface((2, 2))

    def __init__(self, game, position, velocity):
        self.game = game
        self.image = self.image.copy()
        self.image.fill(pg.Color(165, 10, 28))
        self.mask = pg.Mask((1, 1), fill=True)
        self.position = position
        self.velocity = velocity

    def update(self, dt, offset):
        self.velocity.y += 10
        self.position += self.velocity * dt
        if self.collided_with_map(self.position, self.mask, self.game):
            self.game.stain_map(self.position, self.image)
            self.game.remove_object(self)

    def draw(self, surface, offset):
        blit_centered(self.image, surface, self.position - offset)
