import pygame as pg

from src.game import Game

WINDOW_SIZE = (1216, 800)
DISPLAY_SIZE = (608, 400)

pg.init()
screen = pg.display.set_mode(WINDOW_SIZE, 0, 32)

game = Game(screen)
game.run()
