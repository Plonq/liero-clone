# General utils
import functools
import random
import time


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
            # print(next_call_time)
            if time.time() - time_of_last_call > next_call_time:
                func(*args, **kwargs)
                time_of_last_call = time.time()

        return wrapper

    return decorator


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
