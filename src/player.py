import random

from pygame.math import Vector2

from src.engine import Entity
from src.weapons import MachineGun, Weapon


class Player(Entity):
    def __init__(self, game, x=0, y=0):
        super().__init__(game, "player", x, y, 12, 14)
        self.alive = False
        self.current_weapon = Weapon(game, "machine_gun")

    def update(self, boundary_rects, collision_mask, dt):
        if not self.alive:
            return

        self._animate()
        if self.game.input.states["move_left"]:
            self.direction_x = -1
        elif self.game.input.states["move_right"]:
            self.direction_x = 1
        else:
            self.direction_x = 0

        if self.game.input.states["jump"]:
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
        if self.game.input.states["dig"]:
            self.dig()

        self.current_weapon.update(dt)
        if self.game.input.states["attack"]:
            direction = self.game.window.get_mouse_pos() - self.position
            direction.normalize_ip()
            self.current_weapon.attack(self.position, direction)

    def draw(self, surface, offset):
        if not self.alive:
            return
        super().draw(surface, offset)

    def die(self):
        self.alive = False

    def spawn(self):
        position = Vector2(
            random.randint(self.width, self.game.window.display_size[0] - self.width),
            random.randint(self.height, self.game.window.display_size[1] - self.height),
        )
        self.game.world.destroy_terrain(position, radius=self.height * 0.8)
        self.x, self.y = position
        self.alive = True

    def dig(self):
        mouse_pos = self.game.window.get_mouse_pos()
        direction = (mouse_pos + self.game.world.offset - self.position).normalize()
        dig_pos = self.position + (direction * 5)
        self.game.world.destroy_terrain(dig_pos, self.height * 0.8)
