import pygame as pg

from src import assets
from src.engine.game import GameObject
from src.engine.gfx import Effect
from src.engine.utils import blit_centered


class Projectile(GameObject):
    def __init__(self, game, img, start_pos, direction, speed):
        self.game = game
        self.image = img
        self.position = start_pos
        self.direction = direction.normalize()
        self.speed = speed

    def update(self, dt, offset):
        movement = self.direction * self.speed * dt
        self.position += movement
        if self.test_collision(
            self.game.get_collision_rects(), self.game.get_collision_mask()
        ):
            self.explode()
            return
        if not self.game.is_within_map(self.position):
            self.game.remove_object(self)

    def test_collision(self, collision_rects, collision_mask):
        for rect in collision_rects:
            if rect.collidepoint(self.position.x, self.position.y):
                return True
        self_mask = pg.Mask((1, 1), True)
        int_pos = (int(-self.position.x), int(-self.position.y))
        mask_collided = self_mask.overlap(collision_mask, int_pos)
        return mask_collided is not None

    def explode(self):
        self.game.destroy_terrain(self.position, 7)
        self.game.remove_object(self)
        self.game.add_object(
            Effect(
                self.game,
                spritesheet_img=assets.explosion_small,
                image_count=7,
                frame_size=14,
                position=self.position,
                lifespan=0.2,
            )
        )

    def draw(self, surface, offset):
        blit_centered(self.image, surface, self.position - offset)
