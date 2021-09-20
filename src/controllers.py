from src.engine.input import (
    is_action_just_pressed,
    is_action_pressed,
    was_action_just_released,
)


class PlayerController:
    """A controller based on input events (i.e. human player)."""

    def is_action_pressed(self, action):
        return is_action_pressed(action)

    def is_action_just_pressed(self, action):
        return is_action_just_pressed(action)

    def was_action_just_released(self, action):
        return was_action_just_released(action)
