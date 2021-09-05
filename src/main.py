import sys
from itertools import cycle

import pygame as pg

from src import engine as e
from src.constants import DISPLAY_SIZE, ROOT_DIR, WINDOW_SIZE
from src.utils import XY, clamp

clock = pg.time.Clock()

pg.init()
pg.display.set_caption("Liero Clone")

screen = pg.display.set_mode(WINDOW_SIZE, 0, 32)

display = pg.Surface(DISPLAY_SIZE)

e.load_animation_data(ROOT_DIR / "assets/images/entities")

player = e.Entity("player", x=50, y=300, width=16, height=16)
map_boundary_rects = (
    pg.Rect(0, 0, DISPLAY_SIZE[0], 1),
    pg.Rect(0, 0, 1, DISPLAY_SIZE[1]),
    pg.Rect(DISPLAY_SIZE[0] - 1, 0, 1, DISPLAY_SIZE[1]),
    pg.Rect(0, DISPLAY_SIZE[1] - 1, DISPLAY_SIZE[0], 1),
)

map_surf = pg.Surface(DISPLAY_SIZE)
map_surf.set_colorkey((0, 0, 0))
map_surf.fill((179, 78, 31))
map_mask_img = pg.image.load(ROOT_DIR / "assets/images/mask-test.png").convert()
map_mask_img.set_colorkey((0, 0, 0))
map_mask = pg.mask.from_surface(map_mask_img)

true_offset = [0, 0]

last_frame_time = pg.time.get_ticks()

while True:
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

    # map_mask.to_surface(display)
    curr_map = map_surf.copy()
    map_mask.to_surface(curr_map, setcolor=None)
    curr_map.set_colorkey((0, 0, 0))
    display.blit(curr_map, (0, 0))

    # pg.draw.circle(display, (255, 0, 0), (127, 393), 1)
    pg.draw.rect(display, (255, 0, 0), (30, 383, 1, 1))

    player.update(map_boundary_rects, map_mask)
    player.draw(display, offset)

    if hasattr(player, "mask"):
        player.mask.to_surface(display, dest=(player.x, player.y))

    # System
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

    screen.blit(pg.transform.scale(display, WINDOW_SIZE), (0, 0))
    pg.display.update()
    clock.tick(60)
