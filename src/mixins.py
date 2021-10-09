from pygame.math import Vector2


class ParticleCollisionMixin:
    def collided_with_map(self, position, mask, game):
        if not game.is_within_map(position):
            return True
        int_pos = (int(-position.x), int(-position.y))
        has_collided = False
        for game_mask in game.get_collision_masks(combined=False):
            if mask.overlap(game_mask, int_pos) is not None:
                has_collided = True
        return has_collided


class WormCollisionMixin:
    def collided_with_worm(self, position, worm, mask):
        if worm.position.distance_squared_to(position) < 20 ^ 2:
            int_pos = (int(position.x), int(position.y))
            worm_mask = worm.get_current_mask()
            worm_topleft = int(worm.position.x - worm_mask.get_size()[0] / 2), int(
                worm.position.y - worm_mask.get_size()[1] / 2
            )
            mask_offset = Vector2(worm_topleft) - Vector2(int_pos)
            return (
                mask.overlap(worm_mask, (int(mask_offset.x), int(mask_offset.y)))
                is not None
            )
