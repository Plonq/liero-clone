import pygame as pg

from src.assets import Assets
from src.input import Input
from src.window import Window
from src.world import World
from src.player import Player

clock = pg.time.Clock()


class Game:
    def __init__(self):
        self.window = Window(self)
        self.assets = Assets()
        self.input = Input(self)
        self.world = World(self)
        self.player = Player(self)

        self.display = self.window.display

    def update(self):
        self.input.update()
        self.world.update()
        self.player.update(
            self.world.map_boundary_rects, self.world.mask, self.window.dt
        )
        self.window.render_frame()

    def draw(self):
        self.world.draw(self.window.display)
        self.player.draw(self.window.display, self.world.offset)

    def run(self):
        while True:
            self.update()
            self.draw()


Game().run()
