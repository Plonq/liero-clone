import pygame as pg
from pygame.math import Vector2

from src.engine import Entity
from src.weapons import MachineGun


class Player(Entity):
    def __init__(self, game, x, y):
        super().__init__(game, "player", x, y, 12, 14)
        self.has_dug = False
        self.current_weapon = MachineGun()
        self.game.world.destroy_terrain(self.position, radius=self.height * 0.8)

    def update(self, boundary_rects, collision_mask, dt):
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
            if not self.has_dug:
                self.dig()
                self.has_dug = True
        else:
            self.has_dug = False

        if self.game.input.states["fire"]:
            target_pos = self.game.window.get_mouse_pos() + self.game.offset
            self.current_weapon.fire(self.position, target_pos)

        # Update items
        visible_rect = pg.Rect(
            self.game.offset.x,
            self.game.offset.y,
            self.game.window.display_size[0],
            self.game.window.display_size[1],
        )
        self.current_weapon.update(visible_rect, dt)

    def draw(self, surface, offset=(0, 0)):
        super().draw(surface, offset)
        self.current_weapon.draw(surface, offset)

    def dig(self):
        player_pos = self.game.player.position
        mouse_pos = self.game.window.get_mouse_pos()
        direction = (mouse_pos + self.game.offset - player_pos).normalize()
        dig_pos = player_pos + (direction * 5)
        self.game.world.destroy_terrain(dig_pos, self.game.player.height * 0.8)
