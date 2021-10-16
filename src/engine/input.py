import logging

import pygame as pg

logger = logging.getLogger(__name__)


_actions = {"mouse": {}, "key": {}}
_actions_by_name = {}
_mouse_move_hooks = []


def register_action(name, input_type, input_value):
    action = Action(name)
    if input_value not in _actions[input_type]:
        _actions[input_type][input_value] = []
    _actions[input_type][input_value].append(action)
    _actions_by_name[name] = action


def register_mouse_action(name, button):
    register_action(name, "mouse", button)


def register_mouse_move_hook(fn):
    _mouse_move_hooks.append(fn)


def unregister_mouse_move_hook(fn):
    _mouse_move_hooks.remove(fn)


def register_key_action(name, key):
    register_action(name, "key", key)


def is_action_pressed(name):
    action = _get_action(name)
    if not action:
        return False
    return action.is_pressed


def is_action_just_pressed(name):
    action = _get_action(name)
    if not action:
        return False
    return action.is_just_pressed


def was_action_just_released(name):
    action = _get_action(name)
    if not action:
        return False
    return action.was_just_released


def _get_action(name):
    try:
        return _actions_by_name[name]
    except KeyError:
        logger.warning(
            f"Tried to access state of '{name}' but that action hasn't been registered."
        )


def update_input_states():
    """Called every frame, before process_input_events."""
    for input_type in _actions.values():
        for actions in input_type.values():
            for action in actions:
                action.update_state()


def process_input_events(game, input_events):
    """Called every frame with any input events (mouse down, etc)."""
    for event in input_events:
        if event.type == pg.MOUSEBUTTONDOWN:
            for button, actions in _actions["mouse"].items():
                if button == event.button:
                    for action in actions:
                        action.activate()

        if event.type == pg.MOUSEBUTTONUP:
            for button, actions in _actions["mouse"].items():
                if button == event.button:
                    for action in actions:
                        action.deactivate()

        if event.type == pg.MOUSEMOTION:
            for fn in _mouse_move_hooks:
                fn(pos=event.pos, rel=event.rel)

        if event.type == pg.KEYDOWN:
            for key, actions in _actions["key"].items():
                if key == event.key:
                    for action in actions:
                        action.activate()

        if event.type == pg.KEYUP:
            for key, actions in _actions["key"].items():
                if key == event.key:
                    for action in actions:
                        action.deactivate()


class Action:
    def __init__(self, name):
        self.name = name
        self.is_pressed = False
        self.is_just_pressed = False
        self.was_just_released = False
        self.should_deactivate = False

    def activate(self):
        self.is_pressed = True
        self.is_just_pressed = True

    def update_state(self):
        self.is_just_pressed = False
        self.was_just_released = False
        if self.should_deactivate:
            self.should_deactivate = False

    def deactivate(self):
        self.is_pressed = False
        self.should_deactivate = True
        self.was_just_released = True
