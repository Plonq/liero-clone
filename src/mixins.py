from pygame.math import Vector2


class ParticleCollisionMixin:
    def collided_with_map(self, position, mask, game, previous_position=None):
        def is_collided(pos):
            int_pos = (int(-pos.x), int(-pos.y))
            for game_mask in game.get_collision_masks(combined=False):
                if mask.overlap(game_mask, int_pos) is not None:
                    return True
            return False

        if not game.is_within_map(position):
            return position

        collided = is_collided(position)
        if collided:
            if previous_position:
                for i in range(10):
                    pos = previous_position.lerp(position, i / 10)
                    if is_collided(pos):
                        return pos
            else:
                return position

        return None


class WormCollisionMixin:
    def collided_with_worm(self, position, worm, mask, previous_position=None):
        def is_collided(pos):
            int_pos = (int(pos.x), int(pos.y))
            worm_mask = worm.get_current_mask()
            worm_topleft = int(worm.position.x - worm_mask.get_size()[0] / 2), int(
                worm.position.y - worm_mask.get_size()[1] / 2
            )
            mask_offset = Vector2(worm_topleft) - Vector2(int_pos)
            return mask.overlap(worm_mask, (int(mask_offset.x), int(mask_offset.y)))

        if worm.position.distance_squared_to(position) < 10 ** 2:
            collision = is_collided(position)
            if collision:
                if previous_position:
                    for i in range(10):
                        pos = previous_position.lerp(position, i / 10)
                        if is_collided(pos):
                            return pos
                else:
                    return position

            return None
