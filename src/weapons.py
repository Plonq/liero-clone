import random

from src.config import config
from src.projectiles import Projectile


class Weapon:
    def __init__(self, game, type):
        self.game = game
        self.type = type
        self.type = config["weapons"][type]["type"]
        self.bullets_per_round = config["weapons"][type]["bullets_per_round"]
        self.rounds_per_magazine = config["weapons"][type]["rounds_per_magazine"]
        self.reload_time = config["weapons"][type]["reload_time"]
        self.round_cooldown = config["weapons"][type]["round_cooldown"]
        self.bullet_speed = config["weapons"][type]["bullet_speed"]
        self.damage = config["weapons"][type]["damage"]
        self.current_cooldown = 0
        self.image = self.game.assets.basic_projectile

    def update(self, dt):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

    def attack(self, start_pos, direction):
        if self.current_cooldown == 0:
            jitter = random.randrange(-15, 15)
            # direction.rotate_ip(jitter)
            start_pos = start_pos + (direction * 14)
            self.game.world.projectiles.append(
                Projectile(self.image, start_pos, direction)
            )
            self.current_cooldown = self.round_cooldown
