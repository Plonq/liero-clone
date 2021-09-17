import random

from src.assets import get_image
from src.projectile import Projectile


class Weapon:
    def __init__(self, game):
        self.game = game
        self.reload_time = 1


class ProjectileWeapon(Weapon):
    """Basic weapon like minigun or machine gun."""

    def __init__(self, game):
        super().__init__(game)
        self.bullets_per_round = 1
        self.rounds_per_magazine = 1
        self.round_cooldown = 5
        self.bullet_speed = 200
        self.bullet_speed_jitter = 0
        self.accuracy = 0.99
        self.damage_per_bullet = 1
        self.automatic = False
        self.current_cooldown = 0
        self.is_firing = False

    def update(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

    def pull_trigger(self, start_pos, direction):
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
            self.current_cooldown = self.round_cooldown

    def release_trigger(self):
        self.is_firing = False


class Minigun(ProjectileWeapon):
    def __init__(self, game):
        super().__init__(game)
        self.reload_time = 2
        self.bullets_per_round = 1
        self.rounds_per_magazine = 100
        self.round_cooldown = 2
        self.bullet_speed = 200
        self.bullet_speed_jitter = 0
        self.accuracy = 0.99
        self.damage_per_bullet = 1
        self.automatic = True


class Shotgun(ProjectileWeapon):
    def __init__(self, game):
        super().__init__(game)
        self.reload_time = 0.8
        self.bullets_per_round = 20
        self.rounds_per_magazine = 2
        self.round_cooldown = 10
        self.bullet_speed = 300
        self.bullet_speed_jitter = 100
        self.accuracy = 0.93
        self.damage_per_bullet = 3
        self.automatic = False
