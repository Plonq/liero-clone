from pygame.math import Vector2

from src.config import config
from src.engine.entity import Entity
from src.engine.input import is_action_pressed, set_action_state
from src.weapons import Weapon


class Player(Entity):
    def __init__(self, world, x=0, y=0):
        super().__init__(world, "player", x, y, 12, 14)
        self.alive = False
        self.available_weapons = [
            Weapon(world, name) for name in config["weapons"].keys()
        ]
        self.current_weapon = self.available_weapons[0]

    def update(self, boundary_rects, collision_mask, dt):
        if not self.alive:
            return

        self._animate()
        if is_action_pressed("move_left"):
            self.direction_x = -1
        elif is_action_pressed("move_right"):
            self.direction_x = 1
        else:
            self.direction_x = 0

        if is_action_pressed("jump"):
            if self.air_timer < self.jump_buffer:
                self.speed_y = -5

        # Movement
        velocity = Vector2(0)
        velocity.x += self.direction_x * self.run_speed * dt
        velocity.y += self.speed_y * dt

        # Gravity
        self.speed_y += 0.3 * dt
        if self.speed_y > 4:
            self.speed_y = 4

        # Move and hit stuff
        collision_directions = self._move_and_collide(
            velocity, boundary_rects, collision_mask
        )

        # What do if hit stuff?
        if collision_directions["bottom"]:
            self.speed_y = 0
            self.air_timer = 0
        else:
            self.air_timer += 1
        if collision_directions["top"]:
            self.speed_y = 0

        # Actions
        if is_action_pressed("dig"):
            self.dig()

        self.current_weapon.update()
        if is_action_pressed("attack"):
            direction = (
                self.game.get_mouse_pos() + self.game.world.offset - self.position
            )
            direction.normalize_ip()
            can_keep_firing = self.current_weapon.attack(self.position, direction)
            if not can_keep_firing:
                set_action_state("attack", False)

        if is_action_pressed("switch_weapon"):
            index = self.available_weapons.index(self.current_weapon) + 1
            if index > len(self.available_weapons) - 1:
                index = 0
            self.current_weapon = self.available_weapons[index]

    def draw(self, surface, offset):
        if not self.alive:
            return
        super().draw(surface, offset)

    def die(self):
        self.alive = False

    def dig(self):
        mouse_pos = self.game.get_mouse_pos()
        direction = (mouse_pos + self.game.world.offset - self.position).normalize()
        dig_pos = self.position + (direction * 5)
        self.game.world.destroy_terrain(dig_pos, self.height * 0.8)
