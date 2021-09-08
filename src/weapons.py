import random
import pygame as pg


class MachineGun:
    def __init__(self):
        self.image = pg.Surface((1, 1))
        self.image.fill((255, 255, 255))
        self.cooldown = 4
        self.bullet_speed = 2

        self.bullets = []
        self.current_cooldown = self.cooldown

    def fire(self, start_pos, target_pos):
        if self.current_cooldown == 0:
            jitter = random.randrange(-15, 15)
            direction = (target_pos - start_pos).normalize()
            # direction.rotate_ip(jitter)
            start_pos = start_pos + (direction * 14)
            self.bullets.append([start_pos, direction])
            self.current_cooldown = self.cooldown
        else:
            self.current_cooldown -= 1

    def update(self, visible_rect, dt):
        for i, bullet in sorted(enumerate(self.bullets), reverse=True):
            movement = bullet[1] * self.bullet_speed * dt
            bullet[0] += movement
            if not visible_rect.collidepoint(bullet[0].x, bullet[0].y):
                self.bullets.pop(i)

    def draw(self, surface, offset):
        for i, bullet in sorted(enumerate(self.bullets), reverse=True):
            surface.blit(self.image, bullet[0] - offset)
