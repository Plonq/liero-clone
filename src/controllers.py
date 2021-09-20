import random

from src.engine.input import (
    is_action_just_pressed,
    is_action_pressed,
    was_action_just_released,
)


class PlayerController:
    """A controller based on input events (i.e. human player)."""

    def __init__(self, game):
        self.game = game
        self.worm = None

    def set_worm(self, worm):
        self.worm = worm

    def update(self, dt, offset):
        if self.worm is None:
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
            self.worm.dig(offset)

        if is_action_just_pressed("grapple"):
            if self.worm.grapple.launched:
                self.worm.retract_grapple()
            else:
                self.worm.launch_grapple()

        if is_action_pressed("attack"):
            self.worm.pull_trigger()
        if was_action_just_released("attack"):
            self.worm.release_trigger()

        if is_action_just_pressed("switch_weapon"):
            self.worm.next_weapon()


class AiController:
    """A controller based on input events (i.e. human player)."""

    def is_action_pressed(self, action):
        return bool(random.randint(0, 1))

    def is_action_just_pressed(self, action):
        return bool(random.randint(0, 1))

    def was_action_just_released(self, action):

        return bool(random.randint(0, 1))
