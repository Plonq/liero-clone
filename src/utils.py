from collections import namedtuple

Tile = namedtuple("Tile", ("x", "y", "type"))
XY = namedtuple("XY", ("x", "y"))
WH = namedtuple("WH", ("width", "height"))


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)
