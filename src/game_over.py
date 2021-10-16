import pygame as pg
from pygame.math import Vector2

from src.assets import assets
from src.engine.font import Font
from src.engine.game import GameObject
from src.engine.interface import Menu


class GameOver(GameObject):
    def __init__(self, game):
        self.game = game
        self.bg = pg.Surface(self.game.display_size)
        self.bg.fill((150, 150, 150))
        self.center_of_screen = Vector2(
            self.game.display_size[0] // 2, self.game.display_size[1] // 2
        )
        self.small_font = Font(assets["font"]["small"])
        self.large_font = Font(assets["font"]["large"])
        self.spacing = 10
        options = [
            {
                "text": lambda: "Replay",
                "execute": lambda: self.replay(),
            },
            {
                "text": lambda: "Quit",
                "execute": lambda: self.game.quit(),
            },
        ]
        self.center_of_screen = Vector2(
            self.game.display_size[0] // 2, self.game.display_size[1] // 2
        )
        self.menu = Menu(game, options, self.center_of_screen + Vector2(0, 100))
        self.winner = None
        self.loser = None

    def update(self, dt, offset):
        self.menu.update(dt, offset)

    def draw(self, surface, offset):
        surface.blit(self.bg, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
        self.large_font.draw_centered(
            surface,
            "GAME OVER",
            pg.Color("white"),
            self.center_of_screen - Vector2(0, 100),
            scale=2,
        )
        self._draw_winner(surface, offset)
        self.menu.draw(surface, offset)

    def _draw_winner(self, surface, offset):
        self.large_font.draw_centered(
            surface,
            f"{self.winner.name} Wins!",
            pg.Color("white"),
            Vector2(self.center_of_screen),
            scale=1.5,
        )

    def replay(self):
        self.game.reset_game()
        self.game.start_game(multi=self.game.mode == "multi")
