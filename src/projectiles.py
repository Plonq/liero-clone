from src.engine import blit_centered


class Projectile:
    def __init__(self, img, start_pos, direction, speed):
        self.image = img
        self.position = start_pos
        self.direction = direction.normalize()
        self.speed = speed

    def update(self, dt):
        movement = self.direction * self.speed * dt
        self.position += movement

    def draw(self, surface, offset):
        blit_centered(self.image, surface, self.position - offset)
