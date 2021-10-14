import pygame as pg
from pygame.math import Vector2

from src.assets import get_image
from src.engine.game import GameObject
from src.engine.signals import emit_event
from src.engine.utils import blit_centered
from src.gfx import SmallExplosion
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
        if self.collided_with_map(new_position, self.mask, self.game):
            # Find exact point of collision (edge of object)
            for i in range(10):
                pos = self.position.lerp(new_position, i / 10)
                if self.collided_with_map(pos, self.mask, self.game):
                    self.position = pos
                    return {"type": "map"}
        for worm in self.game.get_living_worms():
            if self.collided_with_worm(self.position, worm, self.mask):
                self.position = new_position
                return {"type": "worm", "worm": worm}
        self.position = new_position
        return {"type": None}

    def explode(self):
        self.game.destroy_terrain(self.position, 7)
        self.game.remove_object(self)
        self.game.add_object(SmallExplosion(self.game, self.position))

    def draw(self, surface, offset):
        blit_centered(self.image, surface, self.position - offset)


class Bullet(Projectile):
    def __init__(self, game, worm, start_pos, velocity, damage):
        img = pg.Surface((1, 1)).convert()
        img.fill(pg.Color("white"))
        super().__init__(game, worm, img, start_pos, velocity, damage)

    def update(self, dt, offset):
        collision = self._move_and_collide(dt)
        if collision["type"] == "map":
            self.explode()
        elif collision["type"] == "worm":
            collision["worm"].damage(
                self.damage, self.velocity, attacker=self.worm, location=self.position
            )
            self.game.remove_object(self)


class Rocket(Projectile):
    def __init__(self, game, worm, start_pos, velocity, damage, aoe_range):
        super().__init__(
            game,
            worm,
            get_image("weapons/placeholder.png"),
            start_pos,
            velocity,
            damage,
        )
        self.aoe_range = aoe_range
        self.mask = pg.Mask((5, 5), True)

    def update(self, dt, offset):
        collision = self._move_and_collide(dt)
        if collision["type"]:
            self.explode()

    def explode(self):
        self.game.destroy_terrain(self.position, 20)
        for worm in self.game.get_living_worms():
            dist = self.position.distance_to(worm.position)
            if dist < self.aoe_range:
                dmg = self.damage - int(self.damage * (dist / self.aoe_range))
                worm.damage(dmg, self.velocity, attacker=self.worm)

        self.game.remove_object(self)
