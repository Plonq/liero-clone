import math
import random

from src.config import config
from src.projectile import Projectile


class Weapon:
    def __init__(self, game, name):
        self.game = game
        self.type = config["weapons"][name]["type"]
        self.automatic = config["weapons"][name]["automatic"]
        self.bullets_per_round = config["weapons"][name]["bullets_per_round"]
        self.rounds_per_magazine = config["weapons"][name]["rounds_per_magazine"]
        self.reload_time = config["weapons"][name]["reload_time"]
        self.round_cooldown = config["weapons"][name]["round_cooldown"]
        self.bullet_speed = config["weapons"][name]["bullet_speed"]
        self.bullet_speed_jitter = config["weapons"][name]["bullet_speed_jitter"]
        self.accuracy = config["weapons"][name]["accuracy"]
        self.damage = config["weapons"][name]["damage"]
        self.current_cooldown = 0
        self.image = self.game.assets.basic_projectile

    def update(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

    def attack(self, start_pos, direction):
        if self.current_cooldown == 0:
            angle_offset = round((1 - self.accuracy) * 180)
            for _ in range(self.bullets_per_round):
                angle = random.randint(-angle_offset, angle_offset)
                cur_direction = direction.rotate(angle)
                cur_pos = start_pos + (cur_direction * 14)
                speed_adjustment = (
                    random.randint(-self.bullet_speed_jitter, self.bullet_speed_jitter)
                    / 100
                )
                self.game.add_object(
                    Projectile(
                        self.game,
                        self.image,
                        cur_pos,
                        cur_direction,
                        self.bullet_speed + speed_adjustment,
                    )
                )
            self.current_cooldown = self.round_cooldown
        return self.automatic
