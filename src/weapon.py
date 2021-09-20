import random

from src import config
from src.assets import get_image
from src.engine.signals import emit_event
from src.projectile import Projectile


class Weapon:
    def __init__(self, game, owner, name):
        self.game = game
        self.owner = owner
        self.name = name
        self.type = config.weapons[name]["type"]
        self.automatic = config.weapons[name]["automatic"]
        self.bullets_per_round = config.weapons[name]["bullets_per_round"]
        self.rounds_per_magazine = config.weapons[name]["rounds_per_magazine"]
        self.reload_time = config.weapons[name]["reload_time"]
        self.round_cooldown = config.weapons[name]["round_cooldown"]
        self.bullet_speed = config.weapons[name]["bullet_speed"]
        self.bullet_speed_jitter = config.weapons[name]["bullet_speed_jitter"]
        self.accuracy = config.weapons[name]["accuracy"]
        self.damage = config.weapons[name]["damage"]
        self.current_cooldown = 0
        self.is_firing = False
        self.is_reloading = False
        self.reload_time_elapsed = 0
        self.rounds_left = self.rounds_per_magazine

    def update(self, dt):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
        if self.is_reloading:
            self.reload_time_elapsed += dt
            if self.reload_time_elapsed >= self.reload_time:
                self.is_reloading = False
                self.reload_time_elapsed = 0
                self.rounds_left = self.rounds_per_magazine

    def pull_trigger(self, start_pos, direction):
        if self.is_reloading:
            return
        if not self.automatic and self.is_firing:
            return
        if self.current_cooldown == 0:
            self.is_firing = True
            angle_offset = round((1 - self.accuracy) * 180)
            for _ in range(self.bullets_per_round):
                angle = random.randint(-angle_offset, angle_offset)
                cur_direction = direction.rotate(angle)
                cur_pos = start_pos + (cur_direction * 14)
                speed_adjustment = random.randint(
                    -self.bullet_speed_jitter, self.bullet_speed_jitter
                )
                self.game.add_object(
                    Projectile(
                        self.game,
                        get_image("weapons/basic-projectile.png"),
                        cur_pos,
                        cur_direction,
                        self.bullet_speed + speed_adjustment,
                    )
                )
                emit_event("gunshot", source=self.owner)
            self.current_cooldown = self.round_cooldown
            self.rounds_left -= 1
            if self.rounds_left <= 0:
                self.is_reloading = True

    def release_trigger(self):
        self.is_firing = False
