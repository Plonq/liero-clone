import pygame as pg


class World:
    def __init__(self, game):
        self.game = game
        image = self.game.assets.world_map
        image = image.convert_alpha()
        self.image = image
        self.mask = pg.mask.from_surface(self.image)
        # Helper props
        self.size = image.get_size()

    def _update_mask(self):
        self.mask = pg.mask.from_surface(self.image)

    def destroy_terrain(self, location, radius):
        color = (0, 0, 0, 0)
        pg.draw.circle(self.image, color, location, radius)
        self._update_mask()

    def draw(self, surf, offset):
        x = 0
        y = 0
        x -= offset.x
        y -= offset.y
        surf.blit(self.image, (x, y))
