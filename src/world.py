import pygame as pg

from src.engine.game import GameObject


class World(GameObject):
    def __init__(self, game):
        self.game = game
        image = self.game.assets.world_map
        self.image = image
        self.mask = self.generate_mask()
        self.size = image.get_size()
        self.map_boundary_rects = (
            pg.Rect(-1, -1, self.size[0], 1),
            pg.Rect(-1, -1, 1, self.size[1]),
            pg.Rect(self.size[0], -1, 1, self.size[1]),
            pg.Rect(-1, self.size[1], self.size[0], 1),
        )
        self.projectiles = []

    def update(self, dt, offset):
        self._update_projectiles(dt)

    def draw(self, surface, offset):
        surface.fill((53, 29, 15))
        for map_boundary_rect in self.map_boundary_rects:
            pg.draw.rect(surface, (0, 0, 0), map_boundary_rect)
        surface.blit(self.image, (-offset.x, -offset.y))
        self._draw_projectiles(surface, offset)

    def _update_projectiles(self, dt):
        for i, projectile in sorted(enumerate(self.projectiles), reverse=True):
            projectile.update(dt)
            if not pg.Rect(0, 0, *self.size).collidepoint(
                projectile.position.x, projectile.position.y
            ):
                self.projectiles.pop(i)

    def _draw_projectiles(self, surface, offset):
        for projectile in self.projectiles:
            projectile.draw(surface, offset)

    def generate_mask(self):
        return pg.mask.from_surface(self.image)

    def destroy_terrain(self, location, radius):
        color = (0, 0, 0, 0)
        pg.draw.circle(self.image, color, location, radius)
        self.mask = self.generate_mask()
