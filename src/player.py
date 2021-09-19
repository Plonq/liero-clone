import pygame as pg
from pygame.math import Vector2

from src.assets import get_image
from src.engine.entity import Entity
from src.engine.signals import emit_event
from src.engine.game import GameObject
from src.engine.input import (
    is_action_just_pressed,
    is_action_pressed,
    was_action_just_released,
)
from src.engine.utils import blit_centered, is_same_sign
from src.weapon import Weapon


class Player(Entity):
    def __init__(self, game, x=0, y=0):
        super().__init__(game, "player", x, y, 12, 14)
        self.alive = False
        self.available_weapons = [
            Weapon(game, "super_shotgun"),
            Weapon(game, "minigun"),
            Weapon(game, "shotgun"),
        ]
        self.current_weapon = self.available_weapons[0]
        self.grapple = Grapple(game, self)
        self.terminal_velocity = 300

    def update(self, dt, offset):
        super().update(dt, offset)

        if not self.alive:
            return

        if is_action_pressed("move_left"):
            self.direction_x = -1
        elif is_action_pressed("move_right"):
            self.direction_x = 1
        else:
            self.direction_x = 0

        if is_action_pressed("jump"):
            if self.is_on_ground():
                self.velocity.y = -200
            if self.grapple.stuck:
                self.grapple.retract()

        # Gravity
        self._apply_gravity(6)

        # Actions
        if is_action_just_pressed("dig"):
            self.dig(offset)

        if is_action_just_pressed("grapple"):
            if self.grapple.launched:
                self.grapple.retract()
            else:
                direction = self.game.get_direction_to_mouse(self.position)
                self.grapple.launch(direction)

        self.current_weapon.update(dt)
        if is_action_pressed("attack"):
            direction = self.game.get_direction_to_mouse(self.position)
            self.current_weapon.pull_trigger(self.position, direction)
        if was_action_just_released("attack"):
            self.current_weapon.release_trigger()

        if is_action_just_pressed("switch_weapon"):
            curr_index = self.available_weapons.index(self.current_weapon)
            index = curr_index + 1
            if index >= len(self.available_weapons):
                index = 0
            self.current_weapon = self.available_weapons[index]
            emit_event(
                "switched_weapon",
                previous=self.available_weapons[curr_index],
                current=self.current_weapon,
            )

        self._update_ammo()

    def _update_ammo(self):
        emit_event(
            "ammo",
            self.current_weapon.rounds_left / self.current_weapon.rounds_per_magazine,
        )

    def draw(self, surface, offset):
        if not self.alive:
            return
        super().draw(surface, offset)

    def move(self, collision_rects, collision_masks, dt):
        if self.is_on_ground() and not self.grapple.stuck:
            # Fixed movement on ground
            if self.direction_x != 0:
                self.velocity.x = self.run_speed * self.direction_x
        else:
            if self.grapple.stuck:
                direction_to_grapple = self.grapple.position - self.position
                direction_to_grapple.normalize_ip()
                self.velocity += direction_to_grapple * 17
            elif self.direction_x != 0:
                not_at_max_speed = abs(self.velocity.x) < self.run_speed
                moving_in_same_dir = is_same_sign(self.direction_x, self.velocity.x)
                if not_at_max_speed or not moving_in_same_dir:
                    self.velocity.x += 4 * self.direction_x

        velocity = self.velocity * dt

        collision_directions = self._move_and_collide(
            velocity, collision_rects, collision_masks
        )

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

    def die(self):
        self.alive = False

    def dig(self, offset):
        mouse_pos = self.game.get_mouse_pos()
        direction = (mouse_pos + offset - self.position).normalize()
        dig_pos = self.position + (direction * 5)
        self.game.destroy_terrain(dig_pos, self.height * 0.8)


class Grapple(GameObject):
    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.image = get_image("weapons/grapple.png")
        self.position = Vector2(0, 0)
        self.direction = Vector2(0, 0)
        self.speed = 300
        self.launched = False
        self.stuck = False

    def update(self, dt, offset):
        if self.stuck:
            return
        movement = self.direction * self.speed * dt
        new_position = self.position + movement
        if self.test_collision(new_position):
            # Find exact point of collision (edge of object)
            for i in range(10):
                pos = self.position.lerp(new_position, i / 10)
                if self.test_collision(pos):
                    self.position = pos
                    self.stuck = True
                    return
        self.position = new_position

    def test_collision(self, position):
        for rect in self.game.get_collision_rects():
            if rect.collidepoint(position.x, position.y):
                return True
        self_mask = pg.Mask((1, 1), True)
        int_pos = (int(-position.x), int(-position.y))
        mask_collided = self_mask.overlap(self.game.get_collision_mask(), int_pos)
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
        self.position = self.player.position
        self.direction = direction
        self.game.add_object(self)
        self.launched = True

    def retract(self):
        self.game.remove_object(self)
        self.launched = False
        self.stuck = False
