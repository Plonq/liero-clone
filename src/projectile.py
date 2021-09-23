import pygame as pg
from pygame.math import Vector2

from src.engine.game import GameObject
from src.engine.signals import emit_event
from src.engine.utils import blit_centered
from src.gfx import SmallExplosion


class Projectile(GameObject):
    def __init__(self, game, img, start_pos, direction, speed):
        self.game = game
        self.image = img
        self.mask = pg.Mask((1, 1), True)
        self.position = start_pos
        self.direction = direction.normalize()
        self.speed = speed

    def update(self, dt, offset):
        movement = self.direction * self.speed * dt
        new_position = self.position + movement
        if self.test_collision(new_position):
            # Find exact point of collision (edge of object)
            for i in range(10):
                pos = self.position.lerp(new_position, i / 10)
                if self.test_collision(pos):
                    self.position = pos
                    self.explode()
                    return
        self.has_hit_worm()
        self.position = new_position

    def test_collision(self, position):
        if not self.game.is_within_map(position):
            return True
        int_pos = (int(-position.x), int(-position.y))
        has_collided = False
        for mask in self.game.get_collision_masks():
            if self.mask.overlap(mask, int_pos) is not None:
                has_collided = True
        return has_collided

    def has_hit_worm(self):
        worms = self.game.get_living_worms()
        for worm in worms:
            if worm.position.distance_to(self.position) < 20:
                int_pos = (int(self.position.x), int(self.position.y))
                worm_mask = worm.get_current_mask()
                worm_topleft = int(worm.position.x - worm_mask.get_size()[0] / 2), int(
                    worm.position.y - worm_mask.get_size()[1] / 2
                )
                mask_offset = Vector2(worm_topleft) - Vector2(int_pos)
                if self.mask.overlap(
                    worm_mask, (int(mask_offset.x), int(mask_offset.y))
                ):
                    self.game.remove_object(self)
                    worm.damage(5)

    def explode(self):
        self.game.destroy_terrain(self.position, 7)
        self.game.remove_object(self)
        self.game.add_object(SmallExplosion(self.game, self.position))
        emit_event("small_explosion")

    def draw(self, surface, offset):
        blit_centered(self.image, surface, self.position - offset)
