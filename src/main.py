from time import time

import pygame as pg

from src.constants import DISPLAY_SIZE, WINDOW_SIZE
from src.game import Game

clock = pg.time.Clock()

pg.init()
pg.display.set_caption("Liero Clone")

screen = pg.display.set_mode(WINDOW_SIZE, 0, 32)

display = pg.Surface(DISPLAY_SIZE)

last_time = time()

game = Game()

while True:
    dt = (time() - last_time) * 60
    last_time = time()

    game.next_frame(display, dt)
    game.process_events(pg.event.get())

    screen.blit(pg.transform.scale(display, WINDOW_SIZE), (0, 0))
    pg.display.update()
    clock.tick(60)
