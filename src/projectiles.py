from src.engine import blit_centered


class Projectile:
    def __init__(self, img, start_pos, direction):
        self.image = img
        self.position = start_pos
        self.direction = direction.normalize()
        self.bullet_speed = 2

    def update(self, dt):
        movement = self.direction * self.bullet_speed * dt
        self.position += movement

    def draw(self, surface, offset):
        blit_centered(self.image, surface, self.position - offset)
