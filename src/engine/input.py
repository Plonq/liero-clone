import logging

import pygame as pg


logger = logging.getLogger(__name__)


_actions = {"mouse": {}, "key": {}}
_actions_by_name = {}


def register_action(name, input_type, input_value):
    action = Action(name)
    if input_value not in _actions[input_type]:
        _actions[input_type][input_value] = []
    _actions[input_type][input_value].append(action)
    _actions_by_name[name] = action


def register_mouse_action(name, button):
    register_action(name, "mouse", button)


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


def _get_action(name):
    try:
        return _actions_by_name[name]
    except KeyError:
        logger.warning(
            f"Tried to access state of '{name}' but that action hasn't been registered."
        )


def set_action_state(name, state):
    action = _actions_by_name[name]
    action.activate() if state else action.deactivate()


def process_input_events():
    """This should be called at the beginning of every frame."""
    for input_type in _actions.values():
        for actions in input_type.values():
            for action in actions:
                action.update_is_just_pressed()

    for event in pg.event.get():
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

        if event.type == pg.QUIT:
            pg.quit()
            exit()


class Action:
    def __init__(self, name):
        self.name = name
        self.is_pressed = False
        self.is_just_pressed = False

    def activate(self):
        self.is_pressed = True
        self.is_just_pressed = True

    def update_is_just_pressed(self):
        self.is_just_pressed = False

    def deactivate(self):
        self.is_pressed = False
        self.is_just_pressed = False
