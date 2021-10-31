# General utils
import functools
import random
import time

import math
import pygame as pg
from pygame.math import Vector2

mask_cache = {}


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


def is_same_sign(num1, num2):
    return num1 >= 0 and num2 >= 0 or num1 < 0 and num2 < 0


def throttle(timeout_ms=1, variance=0):
    time_of_last_call = 0

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal time_of_last_call
            next_call_time = (timeout_ms + random.randint(-variance, variance)) / 1000
            if time.time() - time_of_last_call > next_call_time:
                func(*args, **kwargs)
                time_of_last_call = time.time()

        return wrapper

    return decorator


def rad_to_deg(ang_rad):
    return ang_rad * (180 / math.pi)


# Pygame utils


def blit_centered(from_surf, to_surf, position, **kwargs):
    to_x = position.x - from_surf.get_width() // 2
    to_y = position.y - from_surf.get_height() // 2
    to_surf.blit(from_surf, (to_x, to_y), **kwargs)


def blit_aligned(from_surf, to_surf, rect, h_align="center", v_align="center"):
    target_pos = [0, 0]
    if h_align == "center":
        target_pos[0] = rect.center[0] - from_surf.get_width() // 2
    elif h_align == "left":
        target_pos[0] = rect.left
    elif h_align == "right":
        target_pos[0] = rect.right - from_surf.get_width()
    if v_align == "center":
        target_pos[1] = rect.center[0] - from_surf.get_height() // 2
    elif v_align == "top":
        target_pos[1] = rect.top
    elif v_align == "bottom":
        target_pos[1] = rect.bottom - from_surf.get_height()
    to_surf.blit(from_surf, target_pos)


def create_circle_mask(radius):
    if radius not in mask_cache:
        circle_img = pg.Surface((radius * 2, radius * 2))
        circle_img.fill((0, 0, 0))
        circle_img.set_colorkey((0, 0, 0))
        pg.draw.circle(circle_img, (255, 255, 255), (radius, radius), radius)
        mask_cache[radius] = pg.mask.from_surface(circle_img)
    return mask_cache[radius]


def ray_cast(game, from_pos, direction, ignore_worm=None):
    mask = pg.Mask((1, 1), True)
    new_pos = Vector2(from_pos)

    def is_collided_map(pos):
        int_pos = (int(-pos.x), int(-pos.y))
        for game_mask in game.get_collision_masks(combined=False):
            if mask.overlap(game_mask, int_pos) is not None:
                return True
        return False

    def is_collided_worm(pos, worm):
        int_pos = (int(pos.x), int(pos.y))
        worm_mask = worm.get_current_mask()
        worm_topleft = int(worm.position.x - worm_mask.get_size()[0] / 2), int(
            worm.position.y - worm_mask.get_size()[1] / 2
        )
        mask_offset = Vector2(worm_topleft) - Vector2(int_pos)
        return mask.overlap(worm_mask, (int(mask_offset.x), int(mask_offset.y)))

    hit_worm = None
    while True:
        if hit_worm:
            break

        new_pos += direction
        if not game.is_within_map(new_pos):
            break

        collided = is_collided_map(new_pos)
        if collided:
            break
        for worm in game.get_living_worms():
            if worm != ignore_worm:
                if is_collided_worm(new_pos, worm):
                    hit_worm = worm
                    break
    return {
        "point_of_collision": new_pos,
        "type": "worm" if hit_worm else "map",
        "worm": hit_worm,
    }
