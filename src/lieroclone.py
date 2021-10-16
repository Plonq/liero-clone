import pygame as pg
from pygame.math import Vector2

from src import assets
from src.controllers import AiController, NetworkController, PlayerController
from src.engine.game import Game
from src.engine.input import (
    is_action_just_pressed,
    register_key_action,
    register_mouse_action,
)
from src.engine.signals import observe
from src.engine.utils import clamp
from src.game_over import GameOver
from src.hud import HUD
from src.main_menu import MainMenu
from src.network import Network
from src.worm import Worm
from src.map import Map
from src.sound import SoundEffects

WINDOW_SIZE = (1216, 800)
DISPLAY_SIZE = (608, 400)


class LieroClone(Game):
    def __init__(self):
        super().__init__(WINDOW_SIZE, DISPLAY_SIZE, "Liero Clone")
        assets.init()
        self.network = None
        self.map = Map(self)
        self.add_object(self.map)
        self.player = Worm(self, "player", pg.Color("blue"))
        self.player_ctrl = None
        self.opponent = Worm(self, "opponent", pg.Color("red"))
        self.opponent_ctrl = None
        self.add_object(self.player)
        self.add_object(self.opponent)
        self.hud = HUD(self, self.player)
        self.menu = MainMenu(self)
        self.game_over = GameOver(self)
        self._register_actions()
        self.sound = SoundEffects(self, self.player)
        self.true_offset = [0, 0]
        self.state = "menu"
        self.mode = "single"
        observe("game_over", self._on_game_over)

    def _register_actions(self):
        # Menu
        register_key_action("up", pg.K_UP)
        register_key_action("down", pg.K_DOWN)
        register_key_action("left", pg.K_LEFT)
        register_key_action("right", pg.K_RIGHT)
        register_key_action("select", pg.K_RETURN)
        register_key_action("menu", pg.K_ESCAPE)
        register_mouse_action("menu_click", pg.BUTTON_LEFT)
        # In game
        register_mouse_action("attack", pg.BUTTON_LEFT)
        register_mouse_action("dig", pg.BUTTON_RIGHT)
        register_key_action("jump", pg.K_SPACE)
        register_key_action("move_left", pg.K_a)
        register_key_action("move_right", pg.K_d)
        register_key_action("switch_weapon", pg.K_f)
        register_key_action("grapple", pg.K_e)

    def set_state(self, state):
        self.state = state

    def start_game(self, multi=False):
        self.player_ctrl = PlayerController(self, self.player)
        if multi:
            print("starting multiplayer game")
            self.network = Network()
            self.mode = "multi"
            self.opponent_ctrl = NetworkController(self, self.opponent)
            self.opponent.spawn()
        else:
            self.mode = "single"
            self.opponent_ctrl = AiController(self, self.opponent)
        self.set_state("playing")

    def reset_game(self):
        self.game_objects = []
        self.map.reset()
        for worm in [self.player, self.opponent]:
            worm.reset()
        self.add_object(self.map)
        self.add_object(self.player)
        self.add_object(self.opponent)

    def _on_game_over(self, winner, loser):
        self.set_state("over")
        self.game_over.winner = winner

    def pre_update(self, dt, offset):
        if is_action_just_pressed("menu"):
            self.state = "playing" if self.state == "menu" else "menu"

    def _update(self, dt, offset):
        if self.state == "playing":
            super()._update(dt, offset)
            if self.player_ctrl:
                self.player_ctrl.update(dt, offset)
            if self.opponent_ctrl:
                self.opponent_ctrl.update(dt, offset)

            if self.mode == "multi":
                reply = self.network.send(
                    f"{self.network.id}:{self.player.position.x},{self.player.position.y}"
                )
                id, position = reply.split(":")
                self.opponent_ctrl.move(
                    Vector2(
                        float(position.split(",")[0]), float(position.split(",")[1])
                    )
                )

            self.hud.update(dt, offset)
            self.sound.update(dt)
        else:
            if self.state == "menu":
                self.menu.update(dt, offset)
            elif self.state == "over":
                self.game_over.update(dt, offset)

    def _draw(self, surface, offset):
        super()._draw(surface, offset)
        if self.state == "playing":
            self.hud.draw(surface, offset)
        else:
            if self.state == "menu":
                self.menu.draw(surface, offset)
            elif self.state == "over":
                self.game_over.draw(surface, offset)

    def get_visible_rect(self):
        return pg.Rect(
            self.offset.x,
            self.offset.y,
            self.display_size[0],
            self.display_size[1],
        )

    def update_offset(self, dt):
        self.true_offset[0] += (
            self.player.position.x
            - self.true_offset[0]
            - self.display_size[0] / 2
            + self.player.width // 2
        ) / (0.15 / dt)
        self.true_offset[1] += (
            self.player.position.y
            - self.true_offset[1]
            - self.display_size[1] / 2
            + self.player.height // 2
        ) / (0.15 / dt)
        # Clamp to prevent camera going outside map
        self.true_offset[0] = clamp(
            self.true_offset[0], 0, self.map.size[0] - self.display_size[0]
        )
        self.true_offset[1] = clamp(
            self.true_offset[1], 0, self.map.size[1] - self.display_size[1]
        )
        self.offset = Vector2(int(self.true_offset[0]), int(self.true_offset[1]))

    def is_within_map(self, position):
        return self.get_map_rect().collidepoint(position.x, position.y)

    def get_map_rect(self):
        return pg.Rect(0, 0, *self.map.size)

    def get_collision_rects(self):
        return self.map.map_boundary_rects

    def get_collision_mask(self, destructible=True):
        if destructible:
            return self.map.destructible_mask
        return self.map.indestructible_mask

    def get_collision_masks(self, combined=True):
        if combined:
            return self.map.get_collision_mask()
        return self.map.get_collision_masks()

    def get_living_worms(self):
        return [worm for worm in [self.player, self.opponent] if worm.alive]

    def destroy_terrain(self, location, radius):
        self.map.destroy_terrain(location, radius)

    def stain_map(self, position, image):
        self.map.stain_map(position, image)

    def get_player_position(self):
        return self.player.position

    def get_minimap(self):
        return self.map.minimap


if __name__ == "__main__":
    LieroClone().run()
