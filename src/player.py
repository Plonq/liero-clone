from pygame.math import Vector2

from src import config
from src.engine.entity import Entity
from src.engine.input import (
    is_action_just_pressed,
    is_action_pressed,
    set_action_state,
)
from src.weapon import Weapon


class Player(Entity):
    def __init__(self, game, x=0, y=0):
        super().__init__(game, "player", x, y, 12, 14)
        self.alive = False
        self.available_weapons = [Weapon(game, name) for name in config.weapons.keys()]
        self.current_weapon = self.available_weapons[0]

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
                self.speed_y = -300

        # Gravity
        self.speed_y += 18
        if self.speed_y > 240:
            self.speed_y = 240

        # Actions
        if is_action_just_pressed("dig"):
            self.dig(offset)

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
        velocity.x += self.direction_x * self.run_speed * dt
        velocity.y += self.speed_y * dt

        collision_directions = self._move_and_collide(
            velocity, collision_rects, collision_masks
        )

        if collision_directions["bottom"]:
            self.speed_y = 0
            self.air_timer = 0
        else:
            self.air_timer += 1
        if collision_directions["top"]:
            self.speed_y = 0

    def die(self):
        self.alive = False

    def dig(self, offset):
        mouse_pos = self.game.get_mouse_pos()
        direction = (mouse_pos + offset - self.position).normalize()
        dig_pos = self.position + (direction * 5)
        self.game.destroy_terrain(dig_pos, self.height * 0.8)
