import pygame as pg

from src.engine.game import GameObject
from src.engine.utils import blit_centered
from src.gfx import Explosion


class Projectile(GameObject):
    def __init__(self, game, img, start_pos, direction, speed):
        self.game = game
        self.image = img
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
        if not self.game.is_within_map(self.position):
            self.game.remove_object(self)
            return
        self.position = new_position

    def test_collision(self, position):
        for rect in self.game.get_collision_rects():
            if rect.collidepoint(position.x, position.y):
                return True
        self_mask = pg.Mask((1, 1), True)
        int_pos = (int(-position.x), int(-position.y))
        mask_collided = self_mask.overlap(self.game.get_collision_mask(), int_pos)
        return mask_collided is not None

    def explode(self):
        self.game.destroy_terrain(self.position, 7)
        self.game.remove_object(self)
        self.game.add_object(Explosion(self.game, self.position, size="small"))

    def draw(self, surface, offset):
        blit_centered(self.image, surface, self.position - offset)
