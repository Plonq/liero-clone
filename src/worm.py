import random

import pygame as pg
from pygame.math import Vector2

from src.assets import get_image
from src.engine.entity import Entity
from src.engine.signals import emit_event
from src.engine.game import GameObject
from src.engine.utils import blit_centered, is_same_sign
from src.gfx import BloodParticle
from src.weapon import Weapon


class Worm(Entity):
    def __init__(self, game, name, controller, x=0, y=0):
        super().__init__(game, name, x, y, 12, 14)
        self.ctrl = controller
        self.ctrl.set_worm(self)
        self.alive = False
        self.max_health = 500
        self.health = self.max_health
        self.aim_direction = Vector2(0, 0)
        self.available_weapons = [
            Weapon(game, self, "minigun"),
            Weapon(game, self, "shotgun"),
            Weapon(game, self, "super_shotgun"),
        ]
        self.current_weapon = self.available_weapons[0]
        self.grapple = Grapple(game, self)
        self.terminal_velocity = 300

    def update(self, dt, offset):
        super().update(dt, offset)

        if not self.alive:
            return

        self.current_weapon.update(dt)
        self.ctrl.update(dt, offset)

        self._update_ammo()
        self.move(self.game.get_collision_mask(), dt)

    def set_aim_direction(self, direction):
        self.aim_direction = direction.normalize()

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
        self.current_weapon.pull_trigger(self.position, self.aim_direction)

    def pull_and_release_trigger(self):
        self.current_weapon.pull_trigger(self.position, self.aim_direction)
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
            source=self,
        )

    def dig(self):
        dig_pos = self.position + (self.aim_direction * 5)
        self.game.destroy_terrain(dig_pos, self.height * 0.7)

    def _update_ammo(self):
        emit_event(
            "ammo",
            source=self,
            ammo_perc=self.current_weapon.rounds_left
            / self.current_weapon.rounds_per_magazine,
        )

    def move(self, collision_masks, dt):
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

        collision_directions = self._move_and_collide(velocity, collision_masks)

        if collision_directions["bottom"]:
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

    def spawn(self, position):
        self.health = self.max_health
        self.game.destroy_terrain(position, radius=self.height * 0.8)
        self.x, self.y = position
        self.alive = True

    def damage(self, dmg, direction):
        self.health -= dmg
        self.spray_blood(dmg, direction)
        if self.health <= 0:
            self.die()

    def spray_blood(self, dmg, source_direction):
        for _ in range(random.randint(dmg, dmg * 2)):
            angle = random.randint(-45, 45)
            direction = source_direction.rotate(angle)
            self.game.add_object(
                BloodParticle(self.game, self.position, direction.normalize() * 100)
            )

    def die(self):
        self.alive = False
        self.grapple.retract()

    def draw(self, surface, offset):
        if not self.alive:
            return
        super().draw(surface, offset)
        # reticule_pos = self.position - offset + (self.aim_direction * 15)
        # pg.draw.rect(surface, pg.Color("red"), (reticule_pos.x, reticule_pos.y, 4, 4))


class Grapple(GameObject):
    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.image = get_image("weapons/grapple.png")
        self.mask = pg.Mask((1, 1), True)
        self.position = Vector2(0, 0)
        self.direction = Vector2(0, 0)
        self.speed = 300
        self.launched = False
        self.stuck = False
        self.retracting = False

    def update(self, dt, offset):
        if self.stuck and not self.test_collision(self.position):
            self.retract()
        elif self.retracting:
            self.direction = self.player.position - self.position
            vector = self.direction.normalize() * self.speed * 3 * dt
            self.position += vector
            if self.position.distance_to(self.player.position) < 10:
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
            self.position = new_position

    def test_collision(self, position):
        int_pos = (int(-position.x), int(-position.y))
        mask_collided = self.mask.overlap(self.game.get_collision_mask(), int_pos)
        return mask_collided is not None

    def draw(self, surface, offset):
        pg.draw.line(
            surface,
            (80, 80, 80),
            self.player.position - offset,
            self.position - offset,
            3,
        )
        pg.draw.line(
            surface,
            (150, 150, 150),
            self.player.position - offset,
            self.position - offset,
            1,
        )
        blit_centered(self.image, surface, self.position - offset)

    def launch(self, direction):
        if self.retracting:
            self.retracting = False
            self.game.remove_object(self)
        self.position = self.player.position
        self.direction = direction
        self.game.add_object(self)
        self.launched = True

    def retract(self):
        if self.launched:
            self.retracting = True
        self.launched = False
        self.stuck = False
