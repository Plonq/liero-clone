from src.engine.game import GameObject
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
        if not self.game.is_within_map(self.position):
            self.game.remove_object(self)

    def draw(self, surface, offset):
        blit_centered(self.image, surface, self.position - offset)
