from collections import namedtuple

WH = namedtuple("WH", ("width", "height"))


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


def blit_centered(from_surf, to_surf, position):
    to_x = position.x - from_surf.get_width() // 2
    to_y = position.y - from_surf.get_height() // 2
    to_surf.blit(from_surf, (to_x, to_y))


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
