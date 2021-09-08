import json
import random
import pygame as pg

from src.constants import ROOT_DIR


class Weapon:
    def __init__(self, name):
        self.name = name
        data = self._load_data()
        self.type = data[name]["type"]
        self.bullets_per_round = data[name]["bullets_per_round"]
        self.rounds_per_magazine = data[name]["rounds_per_magazine"]
        self.reload_time = data[name]["reload_time"]
        self.round_cooldown = data[name]["round_cooldown"]
        self.bullet_speed = data[name]["bullet_speed"]
        self.damage = data[name]["damage"]

    def _load_data(self):
        with open(ROOT_DIR / "data/weapons.json") as f:
            return json.load(f)


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
