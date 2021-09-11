import pygame as pg


_actions = {}

_states = {
    "spawn": False,
    "jump": False,
    "move_left": False,
    "move_right": False,
    "dig": False,
    "attack": False,
    "switch_weapon": False,
}


def register_action(name, input, type):
    _actions["name"] = input, type


def is_action_pressed(name):
    return _states[name]


def set_action_state(name, state):
    _states[name] = state


def process_input_events():
    """This should be called at the beginning of every frame."""
    _reset_transient_states()
    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == pg.BUTTON_LEFT:
                _states["attack"] = True
            if event.button == pg.BUTTON_RIGHT:
                _states["dig"] = True

        if event.type == pg.MOUSEBUTTONUP:
            if event.button == pg.BUTTON_LEFT:
                _states["attack"] = False

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                _states["spawn"] = True
            if event.key == pg.K_SPACE:
                _states["jump"] = True
            if event.key == pg.K_a:
                _states["move_left"] = True
            if event.key == pg.K_d:
                _states["move_right"] = True
            if event.key == pg.K_e:
                _states["switch_weapon"] = True

        if event.type == pg.KEYUP:
            if event.key == pg.K_a:
                _states["move_left"] = False
            if event.key == pg.K_d:
                _states["move_right"] = False

        if event.type == pg.QUIT:
            pg.quit()
            exit()


def _reset_transient_states():
    _states["jump"] = False
    _states["dig"] = False
    _states["spawn"] = False
    _states["switch_weapon"] = False
