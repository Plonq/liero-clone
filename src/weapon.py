import random
from collections import deque

from pygame.math import Vector2

from src.config import config
from src.assets import get_image
from src.engine.signals import emit_event
from src.projectile import Bullet, Rocket


class Weapon:
    def __init__(self, game, owner, name):
        self.game = game
        self.owner = owner
        self.name = name
        cfg = config["weapons"][name]
        self.projectile_type = cfg["projectile_type"]
        self.automatic = cfg["automatic"]
        self.bullets_per_round = cfg["bullets_per_round"]
        self.rounds_per_magazine = cfg["rounds_per_magazine"]
        self.reload_time = cfg["reload_time"]
        self.round_cooldown = cfg["round_cooldown"]
        self.bullet_speed = cfg["bullet_speed"]
        self.bullet_speed_jitter = cfg["bullet_speed_jitter"]
        self.accuracy = cfg["accuracy"]
        self.damage = cfg["damage"]
        self.aoe_range = cfg["aoe_range"]
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
            self.launch_projectile(cur_pos, start_velocity)
            emit_event("weapon_fired", weapon=self)
        self.rounds_left -= 1
        if self.rounds_left <= 0:
            self.is_reloading = True

    def launch_projectile(self, position, velocity):
        projectile = None
        if self.projectile_type == "bullet":
            projectile = Bullet(
                self.game,
                position,
                velocity,
                self.damage,
            )
        if self.projectile_type == "rocket":
            projectile = Rocket(
                self.game, position, velocity, self.damage, self.aoe_range
            )
        if projectile:
            self.bullet_queue.append(projectile)
