from collections import namedtuple

WH = namedtuple("WH", ("width", "height"))


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)
