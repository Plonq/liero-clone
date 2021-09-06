import random
import sys
from time import time

import pygame as pg
from pygame.math import Vector2

from src.constants import DISPLAY_SIZE, ROOT_DIR, WINDOW_SIZE
from src.engine import DestroyableMap, Entity, load_animation_data
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


load_animation_data(ROOT_DIR / "assets/images/entities")

# Main game components
game_map = DestroyableMap(ROOT_DIR / "assets/images/map.png")
player = Entity("player", x=90, y=50, width=16, height=16)
map_boundary_rects = (
    pg.Rect(0, 0, DISPLAY_SIZE[0], 1),
    pg.Rect(0, 0, 1, DISPLAY_SIZE[1]),
    pg.Rect(DISPLAY_SIZE[0] - 1, 0, 1, DISPLAY_SIZE[1]),
    pg.Rect(0, DISPLAY_SIZE[1] - 1, DISPLAY_SIZE[0], 1),
)

# Spawning
game_map.destroy_terrain((player.x, player.y), player.width)

true_offset = [0, 0]

last_time = time()

# Weapons
bullet_img = pg.Surface((1, 1))
bullet_img.fill((255, 255, 255))
firing_at = None
machine_gun_cooldown = 0
machine_gun_bullets = []
bullet_speed = 2

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

    # Weapons
    if firing_at:
        if machine_gun_cooldown == 0:
            jitter = random.randrange(-15, 15)
            direction = (Vector2(firing_at) - Vector2(player.x, player.y)).normalize()
            # direction.rotate_ip(jitter)
            start_pos = Vector2(player.x, player.y) + (direction * 14)
            machine_gun_bullets.append([start_pos, direction])
            machine_gun_cooldown = 1
        else:
            machine_gun_cooldown -= 1

    for i, bullet in sorted(enumerate(machine_gun_bullets), reverse=True):
        display.blit(bullet_img, bullet[0])
        movement = bullet[1] * bullet_speed * dt
        bullet[0] += movement

    # System
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == pg.BUTTON_LEFT:
                firing_at = mouse_pos_to_display_pos(event.pos)
            if event.button == pg.BUTTON_RIGHT:
                pos = Vector2(player.x, player.y)
                pos.x += 10
                if player.flip:
                    pos.x *= -1
                game_map.destroy_terrain(pos, player.height / 1.2)
        if event.type == pg.MOUSEMOTION and firing_at:
            firing_at = mouse_pos_to_display_pos(event.pos)
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            firing_at = None

    screen.blit(pg.transform.scale(display, WINDOW_SIZE), (0, 0))
    pg.display.update()
    clock.tick(60)
