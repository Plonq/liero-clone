import random
from collections import deque

from pygame.math import Vector2

from src.config import config
from src.assets import get_image
from src.engine.signals import emit_event
from src.projectile import Projectile


class Weapon:
    def __init__(self, game, owner, name):
        self.game = game
        self.owner = owner
        self.name = name
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
        self.is_firing = False
        self.is_reloading = False
        self.reload_time_elapsed = 0
        self.rounds_left = self.rounds_per_magazine
        self.bullet_queue = deque()

    def update(self, dt):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
        if self.is_reloading:
            self.reload_time_elapsed += dt
            if self.reload_time_elapsed >= self.reload_time:
                self.is_reloading = False
                self.reload_time_elapsed = 0
                self.rounds_left = self.rounds_per_magazine
        while len(self.bullet_queue) > 0:
            projectile = self.bullet_queue.popleft()
            projectile.velocity += self.owner.velocity
            self.game.add_object(projectile)

    def pull_trigger(self):
        if self.is_reloading:
            return
        if not self.automatic and self.is_firing:
            return
        if self.current_cooldown == 0:
            self.fire()
            self.current_cooldown = self.round_cooldown

    def release_trigger(self):
        self.is_firing = False

    def fire(self):
        self.is_firing = True
        angle_offset = round((1 - self.accuracy) * 180)
        start_pos = self.owner.position
        fire_direction = Vector2(self.owner.aim_direction)
        for _ in range(self.bullets_per_round):
            angle = random.randint(-angle_offset, angle_offset)
            start_direction = fire_direction.rotate(angle)
            cur_pos = start_pos + (start_direction * 14)
            speed_adjustment = random.randint(
                -self.bullet_speed_jitter, self.bullet_speed_jitter
            )
            start_velocity = start_direction * (self.bullet_speed + speed_adjustment)
            self.bullet_queue.append(
                Projectile(
                    self.game,
                    get_image("weapons/basic-projectile.png"),
                    cur_pos,
                    start_velocity,
                    self.damage,
                )
            )
            emit_event("weapon_fired", weapon=self)
        self.rounds_left -= 1
        if self.rounds_left <= 0:
            self.is_reloading = True
