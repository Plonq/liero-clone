import sys
from time import time
from timeit import timeit

import pygame as pg

from src import engine as e
from src.constants import DISPLAY_SIZE, ROOT_DIR, WINDOW_SIZE
from src.engine import DestroyableMap
from src.utils import XY

clock = pg.time.Clock()

pg.init()
pg.display.set_caption("Liero Clone")

screen = pg.display.set_mode(WINDOW_SIZE, 0, 32)

display = pg.Surface(DISPLAY_SIZE)


def mouse_pos_to_display_pos(pos):
    ratio_x = DISPLAY_SIZE[0] / WINDOW_SIZE[0]
    ratio_y = DISPLAY_SIZE[1] / WINDOW_SIZE[1]
    return pos[0] * ratio_x, pos[1] * ratio_y


e.load_animation_data(ROOT_DIR / "assets/images/entities")

player = e.Entity("player", x=90, y=350, width=16, height=16)
map_boundary_rects = (
    pg.Rect(0, 0, DISPLAY_SIZE[0], 1),
    pg.Rect(0, 0, 1, DISPLAY_SIZE[1]),
    pg.Rect(DISPLAY_SIZE[0] - 1, 0, 1, DISPLAY_SIZE[1]),
    pg.Rect(0, DISPLAY_SIZE[1] - 1, DISPLAY_SIZE[0], 1),
)

game_map = DestroyableMap(ROOT_DIR / "assets/images/map-test.png")

true_offset = [0, 0]

last_time = time()


while True:
    dt = (time() - last_time) * 60
    last_time = time()

    display.fill((53, 29, 15))

    # Camera follow player
    player_rect = player.rect
    # true_offset[0] += (
    #     player_rect.x - true_offset[0] - 300 + player_rect.width // 2
    # ) / 15
    # true_offset[1] += (
    #     player_rect.y - true_offset[1] - 200 + player_rect.height // 2
    # ) / 15
    # Clamp to prevent camera going outside map
    # true_offset[0] = clamp(true_offset[0], 0, game_map.dimensions[0] - DISPLAY_SIZE[0])
    # true_offset[1] = clamp(true_offset[1], 0, game_map.dimensions[1] - DISPLAY_SIZE[1])
    offset = XY(int(true_offset[0]), int(true_offset[1]))

    # Map and player
    for map_boundary_rect in map_boundary_rects:
        pg.draw.rect(display, (0, 0, 0), map_boundary_rect)

    game_map.draw(display)

    player.update(map_boundary_rects, game_map.mask, dt)
    player.draw(display, offset)

    # System
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

    screen.blit(pg.transform.scale(display, WINDOW_SIZE), (0, 0))
    pg.display.update()
    clock.tick(60)
