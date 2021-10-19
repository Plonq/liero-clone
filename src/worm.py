import math
import random
from math import atan2

import pygame as pg
from pygame.math import Vector2

from src.assets import get_image
from src.engine.entity import Entity
from src.engine.signals import emit_event, observe
from src.engine.game import GameObject
from src.engine.utils import blit_centered, is_same_sign
from src.gfx import BloodParticle
from src.mixins import WormCollisionMixin
from src.weapon import Weapon


class Worm(Entity):
    max_lives = 1  # TODO
    max_health = 500

    def __init__(self, game, name, color, x=0, y=0):
        super().__init__(game, name, x, y, 12, 14)
        self.z_index = 100
        self.color = color
        self.alive = False
        self.lives = self.max_lives
        self.kills = 0
        self.health = self.max_health
        self.spawn_cooldown = 5
        self.spawn_timer = 0
        self.spawning = False
        self.available_weapons = [
            Weapon(game, self, "minigun"),
            Weapon(game, self, "shotgun"),
            Weapon(game, self, "rpg"),
            Weapon(game, self, "super_shotgun"),
        ]
        self.current_weapon = self.available_weapons[0]
        self.grapple = Grapple(game, self)
        self.terminal_velocity = 300
        self.weapon_img = get_image("entities/player/weapon.png").convert()
        self.weapon_img.set_colorkey(pg.Color("black"))
        self.muzzle_flash_img = get_image("weapons/muzzle-flash.png").convert()
        self.muzzle_flash_img.set_colorkey(pg.Color("black"))
        self.should_muzzle_flash = False
        self.muzzle_flashed_time = 0
        observe("weapon_fired", self._on_weapon_fired)

    def update(self, dt, offset):
        super().update(dt, offset)

        if not self.alive:
            self.spawn_timer = max(0, self.spawn_timer - dt)
            return

        self.move(self.game.get_collision_rects(), self.game.get_collision_masks(), dt)

        self.current_weapon.update(dt)

        self.muzzle_flashed_time += dt
        if self.muzzle_flashed_time > 0.1:
            self.should_muzzle_flash = False

        emit_event(
            "cast_shadow",
            mask=self.get_current_mask(),
            position=self.position,
            centered=True,
        )

    def set_aim_direction(self, direction):
        self.aim_direction = direction.normalize()
        if self.aim_direction.x < 0:
            self.flip = True
        elif self.aim_direction.x > 0:
            self.flip = False

    def move_right(self):
        self.direction_x = 1

    def move_left(self):
        self.direction_x = -1

    def stop(self):
        self.direction_x = 0

    def jump(self):
        if self.is_on_ground():
            self.velocity.y = -200
        if self.grapple.stuck:
            self.grapple.retract()

    def launch_grapple(self):
        self.grapple.retract()
        self.grapple.launch(self.aim_direction)

    def retract_grapple(self):
        self.grapple.retract()

    def pull_trigger(self):
        self.current_weapon.pull_trigger()

    def pull_and_release_trigger(self):
        self.current_weapon.pull_trigger()
        self.current_weapon.release_trigger()

    def release_trigger(self):
        self.current_weapon.release_trigger()

    def next_weapon(self):
        curr_index = self.available_weapons.index(self.current_weapon)
        index = curr_index + 1
        if index >= len(self.available_weapons):
            index = 0
        self.current_weapon = self.available_weapons[index]
        emit_event(
            "switched_weapon",
            previous=self.available_weapons[curr_index],
            current=self.current_weapon,
            worm=self,
        )

    def dig(self):
        dig_pos = self.position + (self.aim_direction * 5)
        self.game.destroy_terrain(dig_pos, self.height * 0.8)

    def move(self, collision_rects, collision_masks, dt):
        if self.is_on_ground() and not self.grapple.stuck:
            # Fixed movement on ground
            if self.direction_x != 0:
                self.velocity.x = self.run_speed * self.direction_x
        else:
            if self.grapple.stuck:
                direction_to_grapple = self.grapple.position - self.position
                direction_to_grapple.normalize_ip()
                self.velocity += direction_to_grapple * 12
            not_at_max_speed = abs(self.velocity.x) < self.run_speed
            moving_in_same_dir = is_same_sign(self.direction_x, self.velocity.x)
            if not_at_max_speed or not moving_in_same_dir:
                self.velocity.x += 4 * self.direction_x
            self._apply_x_resistance(0.5)
            self._apply_y_resistance(0.5)

        self._apply_gravity(6)
        velocity = self.velocity * dt

        collision_directions = self._move_and_collide(
            velocity, collision_rects, collision_masks
        )

        if collision_directions["bottom"]:
            if abs(self.velocity.y) > 250:
                emit_event("worm_impact", worm=self)
                self.velocity.y = self.velocity.y * -0.5
            else:
                self.velocity.y = 0
            self.air_timer = 0
            self._apply_x_resistance(40)
        else:
            self.air_timer += 1
        if collision_directions["top"]:
            self.velocity.y = 0
        if collision_directions["left"]:
            self.velocity.x = 0
        if collision_directions["right"]:
            self.velocity.x = 0

    def _apply_gravity(self, amount):
        self.velocity.y += amount
        if self.velocity.y > 350:
            self.velocity.y = 350

    def _apply_x_resistance(self, amount):
        if self.velocity.x > 0:
            self.velocity.x -= amount
        if self.velocity.x < 0:
            self.velocity.x += amount
        if -amount < self.velocity.x < amount:
            self.velocity.x = 0

    def _apply_y_resistance(self, amount):
        if self.velocity.y > 0:
            self.velocity.y -= amount
        if self.velocity.y < 0:
            self.velocity.y += amount
        if -amount < self.velocity.y < amount:
            self.velocity.y = 0

    def spawn(self):
        if self.spawn_timer > 0:
            return

        def rand_spawn_location():
            return Vector2(
                random.randint(self.width, self.game.display_size[0] - self.width),
                random.randint(self.height, self.game.display_size[1] - self.height),
            )

        self.position = rand_spawn_location()
        while self._collided_with_mask(
            self.game.get_collision_mask(destructible=False)
        ):
            self.position = rand_spawn_location()
        self.health = self.max_health
        self.game.destroy_terrain(self.position, radius=self.height * 0.8)
        self.alive = True
        self.spawning = True

    def damage(self, dmg, direction, attacker, location=None):
        self.health -= dmg
        amount = dmg // 5 + random.randint(1, 2)
        self.spray_blood(direction, location, amount=amount)
        emit_event("worm_damaged", dmg=dmg, worm=self)
        if self.health <= 0:
            self.die(killer=attacker)

    def spray_blood(self, source_direction, from_position=None, arc_angle=45, amount=2):
        for _ in range(amount):
            angle = random.randint(-arc_angle, arc_angle)
            direction = source_direction.rotate(angle)
            self.game.add_object(
                BloodParticle(
                    self.game,
                    Vector2(from_position) if from_position else Vector2(self.position),
                    direction.normalize() * 50,
                    drip=True,
                )
            )

    def die(self, killer):
        self.spray_blood(Vector2(1), self.position, arc_angle=180, amount=150)
        self.grapple.retract()
        self.alive = False
        self.velocity = Vector2(0)
        self.lives -= 1
        self.spawn_timer = self.spawn_cooldown
        killer.kills += 1
        emit_event("worm_died", worm=self, killer=killer)
        if self.lives <= 0:
            emit_event("game_over", winner=killer, loser=self)

    def _on_weapon_fired(self, weapon):
        if not weapon.owner == self:
            return
        self.should_muzzle_flash = True
        self.muzzle_flashed_time = 0

    def reset(self):
        self.alive = False
        self.lives = self.max_lives
        self.health = self.max_health
        self.kills = 0
        self.current_weapon = self.available_weapons[0]
        self.spawn_cooldown = 5
        self.spawn_timer = 0
        self.spawning = False

    def draw(self, surface, offset):
        if not self.alive:
            return

        super().draw(surface, offset)

        # Weapon
        rotation = (
            atan2(self.aim_direction.x, self.aim_direction.y) * (180 / math.pi) - 90
        )
        rotated_weapon_img = pg.transform.rotate(
            pg.transform.flip(self.weapon_img, False, self.flip), rotation
        )
        blit_centered(rotated_weapon_img, surface, self.position - offset)
        if self.should_muzzle_flash:
            rotated_muzzle_flash_img = pg.transform.rotate(
                self.muzzle_flash_img, rotation
            )
            blit_centered(rotated_muzzle_flash_img, surface, self.position - offset)

        # Reticule
        reticule_pos = self.position - offset + (self.aim_direction * 35)
        reticule_pos = Vector2(int(reticule_pos.x), int(reticule_pos.y))
        pg.draw.circle(surface, pg.Color("red"), reticule_pos, 1)


class Grapple(WormCollisionMixin, GameObject):
    def __init__(self, game, worm):
        self.game = game
        self.z_index = 90
        self.worm = worm
        self.image = get_image("weapons/grapple.png")
        self.mask = pg.Mask((1, 1), True)
        self.position = Vector2(0, 0)
        self.direction = Vector2(0, 0)
        self.speed = 500
        self.launched = False
        self.stuck = False
        self.retracting = False
        self.stuck_to_worm = None

    def update(self, dt, offset):
        if self.stuck_to_worm:
            self.position = Vector2(self.stuck_to_worm.position)
        elif self.stuck and not self.test_collision(self.position):
            self.retract()
        elif self.retracting:
            self.direction = self.worm.position - self.position
            vector = self.direction.normalize() * self.speed * 3 * dt
            self.position += vector
            if self.position.distance_to(self.worm.position) < self.speed * 3 * dt:
                self.game.remove_object(self)
                self.retracting = False
        else:
            vector = self.direction * self.speed * dt
            new_position = self.position + vector
            # Find collision between current and new position (prevents going through small chunks of dirt)
            for i in range(10):
                pos = self.position.lerp(new_position, i / 10)
                if self.test_collision(pos):
                    self.position = pos
                    self.stuck = True
                    return
            for worm in self.game.get_living_worms():
                if worm == self.worm:
                    continue
                if self.collided_with_worm(self.position, worm, self.mask):
                    self.stuck = True
                    self.stuck_to_worm = worm
            self.position = new_position

    def test_collision(self, position):
        if not self.game.is_within_map(position):
            return True
        int_pos = (int(-position.x), int(-position.y))
        mask_collided = self.mask.overlap(self.game.get_collision_masks(), int_pos)
        return mask_collided is not None

    def draw(self, surface, offset):
        pg.draw.line(
            surface,
            (80, 80, 80),
            self.worm.position - offset,
            self.position - offset,
            3,
        )
        pg.draw.line(
            surface,
            (150, 150, 150),
            self.worm.position - offset,
            self.position - offset,
            1,
        )
        blit_centered(self.image, surface, self.position - offset)

    def launch(self, direction):
        if self.retracting:
            self.retracting = False
            self.game.remove_object(self)
        self.position = self.worm.position
        self.direction = direction
        self.game.add_object(self)
        self.launched = True
        emit_event("grapple_launched", grapple=self)

    def retract(self):
        if self.launched:
            self.retracting = True
        self.launched = False
        self.stuck = False
        self.stuck_to_worm = None

    def remove(self):
        self.game.remove_object(self)
