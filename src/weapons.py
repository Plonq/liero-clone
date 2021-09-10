import random
import pygame as pg

from src.config import config
from src.projectiles import Projectile


class Weapon:
    def __init__(self, name):
        self.name = name
        self.type = config["weapons"][name]["type"]
        self.bullets_per_round = config["weapons"][name]["bullets_per_round"]
        self.rounds_per_magazine = config["weapons"][name]["rounds_per_magazine"]
        self.reload_time = config["weapons"][name]["reload_time"]
        self.round_cooldown = config["weapons"][name]["round_cooldown"]
        self.bullet_speed = config["weapons"][name]["bullet_speed"]
        self.damage = config["weapons"][name]["damage"]
        # TODO: Implement this


class MachineGun:
    def __init__(self, game):
        self.game = game
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
            self.game.world.projectiles.append(
                Projectile(self.image, start_pos, direction)
            )
            self.current_cooldown = self.cooldown
        else:
            self.current_cooldown -= 1
