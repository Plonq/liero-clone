import pygame as pg
from pygame.math import Vector2

from src import config
from src.assets import get_image
from src.engine.entity import Entity
from src.engine.game import GameObject
from src.engine.input import (
    is_action_just_pressed,
    is_action_pressed,
    set_action_state,
)
from src.engine.utils import blit_centered
from src.weapon import Weapon


class Player(Entity):
    def __init__(self, game, x=0, y=0):
        super().__init__(game, "player", x, y, 12, 14)
        self.alive = False
        self.available_weapons = [Weapon(game, name) for name in config.weapons.keys()]
        self.current_weapon = self.available_weapons[0]
        self.grapple = Grapple(game, self)

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
            if self.air_timer < self.jump_buffer:
                self.momentum.y = -300
            if self.grapple.launched:
                self.grapple.retract()

        # Gravity
        if not self.grapple.stuck:
            self.momentum.y += 18
            if self.momentum.y > 240:
                self.momentum.y = 240
            if self.momentum.x > 0:
                self.momentum.x -= 3
            if self.momentum.x < 0:
                self.momentum.x += 3
            if -3 < self.momentum.x < 3:
                self.momentum.x = 0

        # Actions
        if is_action_just_pressed("dig"):
            self.dig(offset)

        if is_action_just_pressed("grapple"):
            if self.grapple.launched:
                self.grapple.retract()
            else:
                direction = self.game.get_direction_to_mouse(self.position)
                self.grapple.launch(direction)

        self.current_weapon.update()
        if is_action_pressed("attack"):
            direction = self.game.get_mouse_pos() + offset - self.position
            direction.normalize_ip()
            can_keep_firing = self.current_weapon.attack(self.position, direction)
            if not can_keep_firing:
                set_action_state("attack", False)

        if is_action_just_pressed("switch_weapon"):
            index = self.available_weapons.index(self.current_weapon) + 1
            if index >= len(self.available_weapons):
                index = 0
            self.current_weapon = self.available_weapons[index]

    def draw(self, surface, offset):
        if not self.alive:
            return
        super().draw(surface, offset)

    def move(self, collision_rects, collision_masks, dt):
        velocity = Vector2(0)
        if self.grapple.stuck:
            direction_to_grapple = self.grapple.position - self.position
            direction_to_grapple.normalize_ip()
            self.momentum += direction_to_grapple * 10
            # Normal gravity is disabled, but we want a little bit to make things feel right
            self.momentum.y += 3
            if self.momentum.y > 40:
                self.momentum.y = 40
        else:
            velocity.x += self.direction_x * self.run_speed * dt

        velocity += self.momentum * dt

        collision_directions = self._move_and_collide(
            velocity, collision_rects, collision_masks
        )

        if collision_directions["bottom"]:
            self.momentum.y = 0
            self.air_timer = 0
            if self.momentum.x > 0:
                self.momentum.x -= 50
            if self.momentum.x < 0:
                self.momentum.x += 50
            if -50 < self.momentum.x < 50:
                self.momentum.x = 0
        else:
            self.air_timer += 1
        if collision_directions["top"]:
            self.momentum.y = 0
        if collision_directions["left"]:
            self.momentum.x = 0
        if collision_directions["right"]:
            self.momentum.x = 0

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
        self.speed = 250
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
