from src.assets import Assets
from src.input import Input
from src.window import Window
from src.world import World


class Game:
    def __init__(self):
        self.window = Window(self)
        self.assets = Assets()
        self.input = Input(self)
        self.world = World(self)

    def update(self):
        self.input.update()
        self.world.update()
        self.window.render_frame()

    def draw(self):
        self.world.draw(self.window.display)

    def run(self):
        while True:
            self.update()
            self.draw()


Game().run()
