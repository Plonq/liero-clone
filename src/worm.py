import math
import random
from math import atan2

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
        self.z_index = 100
        self.ctrl = controller
        self.ctrl.set_worm(self)
        self.alive = False
        self.max_health = 500
        self.lives = 5
        self.health = self.max_health
        self.aim_direction = Vector2(0, 0)
        self.available_weapons = [
            Weapon(game, self, "minigun"),
            Weapon(game, self, "shotgun"),
            Weapon(game, self, "rpg"),
            Weapon(game, self, "super_shotgun"),
        ]
        self.current_weapon = self.available_weapons[0]
        self.grapple = Grapple(game, self)
        self.terminal_velocity = 300
        self.spawn_cooldown = 5
        self.spawn_timer = 0
        self.spawning = False
        self.weapon_img = get_image("entities/player/weapon.png").convert()
        self.weapon_img.set_colorkey(pg.Color("black"))

    def update(self, dt, offset):
        super().update(dt, offset)

        self.ctrl.update(dt, offset)

        if not self.alive:
            self.spawn_timer = max(0, self.spawn_timer - dt)
            return

        self.move(self.game.get_collision_rects(), self.game.get_collision_masks(), dt)

        self.current_weapon.update(dt)

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
            if abs(self.velocity.y) > 150:
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

    def damage(self, dmg, direction, location=None):
        self.health -= dmg
        amount = dmg // 5 + random.randint(1, 2)
        self.spray_blood(direction, location, amount=amount)
        emit_event("worm_damaged", dmg=dmg, worm=self)
        if self.health <= 0:
            self.die()

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

    def die(self):
        self.spray_blood(Vector2(1), self.position, arc_angle=180, amount=150)
        self.grapple.retract()
        self.alive = False
        self.velocity = Vector2(0)
        self.lives -= 1
        self.spawn_timer = self.spawn_cooldown
        emit_event("worm_died", worm=self)
        if self.lives <= 0:
            print("game over")

    def draw(self, surface, offset):
        if not self.alive:
            return

        super().draw(surface, offset)
        rotation = (
            atan2(self.aim_direction.x, self.aim_direction.y) * (180 / math.pi) - 90
        )
        rotated_weapon_img = pg.transform.rotate(self.weapon_img, rotation)
        blit_centered(rotated_weapon_img, surface, self.position - offset)

        reticule_pos = self.position - offset + (self.aim_direction * 25)
        pg.draw.rect(
            surface,
            pg.Color("red"),
            (int(reticule_pos.x), int(reticule_pos.y), 2, 2),
        )


class Grapple(GameObject):
    def __init__(self, game, player):
        self.game = game
        self.z_index = 90
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
            if self.position.distance_to(self.player.position) < self.speed * 3 * dt:
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
        if not self.game.is_within_map(position):
            return True
        int_pos = (int(-position.x), int(-position.y))
        mask_collided = self.mask.overlap(self.game.get_collision_masks(), int_pos)
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
        emit_event("grapple_launched", grapple=self)

    def retract(self):
        if self.launched:
            self.retracting = True
        self.launched = False
        self.stuck = False

    def remove(self):
        self.game.remove_object(self)
