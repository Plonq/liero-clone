from src.engine import Entity


class Player(Entity):
    def __init__(self, x, y):
        super().__init__("player", x, y, 12, 14)
