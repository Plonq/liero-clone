from pygame.math import Vector2

from src.engine.input import (
    is_action_just_pressed,
    is_action_pressed,
    was_action_just_released,
)


class Controller:
    """Something that can control a worm."""

    def __init__(self, game):
        self.game = game
        self.worm = None

    def set_worm(self, worm):
        self.worm = worm

    def update(self, dt, offset):
        pass


class PlayerController(Controller):
    """A controller based on input events (i.e. human player)."""

    def update(self, dt, offset):
        if self.worm is None:
            return

        if not self.worm.alive and is_action_just_pressed("attack"):
            self.worm.spawn()
            return

        self.worm.set_aim_direction(
            self.game.get_direction_to_mouse(self.worm.position)
        )

        if is_action_pressed("move_left"):
            self.worm.move_left()
        elif is_action_pressed("move_right"):
            self.worm.move_right()
        else:
            self.worm.stop()

        if is_action_just_pressed("jump"):
            self.worm.jump()

        if is_action_just_pressed("dig"):
            self.worm.dig()

        if is_action_just_pressed("grapple"):
            if self.worm.grapple.launched:
                self.worm.retract_grapple()
            else:
                self.worm.launch_grapple()

        if is_action_pressed("attack") and not self.worm.spawning:
            self.worm.pull_trigger()
        if was_action_just_released("attack"):
            self.worm.spawning = False
            self.worm.release_trigger()

        if is_action_just_pressed("switch_weapon"):
            self.worm.next_weapon()


class AiController(Controller):
    """An AI controller."""

    def __init__(self, game):
        super().__init__(game)
        self.last_pos = Vector2(0, 0)
        self.time_at_current_pos = 0

    def update(self, dt, offset):
        if not self.worm.alive:
            self.worm.spawn()

        if not self.game.player.alive:
            return

        if (self.worm.position - self.last_pos).magnitude() < 1:
            self.time_at_current_pos += dt
        else:
            self.time_at_current_pos = 0
        self.last_pos = Vector2(self.worm.position)

        direction_to_player = self.game.player.position - self.worm.position
        direction_to_player.normalize_ip()
        self.worm.set_aim_direction(direction_to_player)

        distance_to_player = self.worm.position.distance_to(self.game.player.position)

        if distance_to_player > 50:
            if direction_to_player.x > 0.2:
                self.worm.move_right()
            elif direction_to_player.x < -0.2:
                self.worm.move_left()
        else:
            self.worm.stop()

        if distance_to_player < 100:
            self.worm.pull_and_release_trigger()

        if self.time_at_current_pos > 0.2:
            self.worm.dig()
