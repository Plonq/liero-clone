import pygame as pg
from pygame.math import Vector2

from src.engine.game import GameObject
from src.engine.signals import emit_event
from src.engine.utils import blit_centered
from src.gfx import SmallExplosion
from src.mixins import ParticleCollisionMixin, WormCollisionMixin


class Projectile(ParticleCollisionMixin, WormCollisionMixin, GameObject):
    def __init__(self, game, img, start_pos, direction, speed, damage):
        self.game = game
        self.image = img
        self.mask = pg.Mask((1, 1), True)
        self.position = start_pos
        self.direction = direction.normalize()
        self.speed = speed
        self.damage = damage

    def update(self, dt, offset):
        movement = self.direction * self.speed * dt
        new_position = self.position + movement
        if self.collided_with_map(new_position, self.mask, self.game):
            # Find exact point of collision (edge of object)
            for i in range(10):
                pos = self.position.lerp(new_position, i / 10)
                if self.collided_with_map(pos, self.mask, self.game):
                    self.position = pos
                    self.explode()
                    return
        for worm in self.game.get_living_worms():
            if self.collided_with_worm(self.position, worm, self.mask):
                worm.damage(self.damage, self.direction, self.position)
                self.game.remove_object(self)
        self.position = new_position

    def explode(self):
        self.game.destroy_terrain(self.position, 7)
        self.game.remove_object(self)
        self.game.add_object(SmallExplosion(self.game, self.position))
        emit_event("small_explosion")

    def draw(self, surface, offset):
        blit_centered(self.image, surface, self.position - offset)
