import pygame as pg


class Input:
    def __init__(self, game):
        self.game = game
        self.states = {
            "spawn": False,
            "jump": False,
            "move_left": False,
            "move_right": False,
            "dig": False,
            "fire": False,
        }

    def update(self):
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == pg.BUTTON_LEFT:
                    self.states["fire"] = True
                if event.button == pg.BUTTON_RIGHT:
                    self.states["dig"] = True

            if event.type == pg.MOUSEBUTTONUP:
                if event.button == pg.BUTTON_LEFT:
                    self.states["fire"] = False
                if event.button == pg.BUTTON_RIGHT:
                    self.states["dig"] = False

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    self.states["spawn"] = True
                if event.key == pg.K_SPACE:
                    self.states["jump"] = True
                if event.key == pg.K_a:
                    self.states["move_left"] = True
                if event.key == pg.K_d:
                    self.states["move_right"] = True

            if event.type == pg.KEYUP:
                if event.key == pg.K_RETURN:
                    self.states["spawn"] = False
                if event.key == pg.K_SPACE:
                    self.states["jump"] = False
                if event.key == pg.K_a:
                    self.states["move_left"] = False
                if event.key == pg.K_d:
                    self.states["move_right"] = False

            if event.type == pg.QUIT:
                pg.quit()
                exit()
