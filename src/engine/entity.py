import json
import os

import pygame as pg
from pygame.math import Vector2

from .game import GameObject
from .sprite import SpriteSheetExtractor
from .utils import blit_aligned


animations = {}


class Entity(GameObject):
    def __init__(self, game, name, x=0, y=0, width=1, height=1):
        self.game = game
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.run_speed = 60
        self.air_timer = 0
        self.jump_buffer = 6
        self.direction_x = 0
        self.velocity = Vector2(0, 0)
        self.action = "idle"
        self.frame = 0
        self.time_since_last_frame = 0
        self.frames_since_idle = 0
        self.flip = False
        self.img = pg.transform.flip(
            animations[self.name][self.action][self.frame]["img"],
            self.flip,
            False,
        )
        self.mask = pg.mask.Mask(self.rect.size, True)

    @property
    def rect(self):
        rect = pg.Rect(0, 0, self.width, self.height)
        rect.center = (self.x, self.y)
        return rect

    @property
    def hit_box_top_left(self):
        # return int(self.x), int(self.y)
        x = self.x - (self.width // 2)
        y = self.y - (self.height // 2)
        return int(x), int(y)

    @property
    def position(self):
        return Vector2(self.x, self.y)

    def update(self, dt, offset):
        self._animate(dt)

    def is_on_ground(self):
        return self.air_timer < self.jump_buffer

    def draw(self, surface, offset):
        offset_rect = self.rect
        offset_rect.center = (self.x, self.y)
        offset_rect.x -= offset[0]
        offset_rect.y -= offset[1]
        blit_aligned(self.img, surface, offset_rect, h_align="center", v_align="bottom")
        # pg.draw.rect(surface, (255, 0, 0), offset_rect, 1)
        # pg.draw.rect(surface, (0, 255, 0), (self.x, self.y, 1, 1))

    def _set_action(self, action):
        if action in animations[self.name]:
            if self.action != action:
                self.action = action
                self.frame = 0
                self.time_since_last_frame = 0

    def _animate(self, dt):
        self.time_since_last_frame += dt

        # Facing left or right?
        if self.direction_x < 0:
            self.frames_since_idle = 0
            self.flip = True
        elif self.direction_x > 0:
            self.frames_since_idle = 0
            self.flip = False

        # In the air?
        if self.air_timer > self.jump_buffer:
            if self.velocity.y < 0:
                self._set_action("jump")
            elif self.velocity.y > 0:
                self._set_action("fall")
        else:
            # Must be on ground
            if self.direction_x < 0 or self.direction_x > 0:
                self.frames_since_idle = 0
                self._set_action("run")
            else:
                # Must be idle
                if self.frames_since_idle < 240:
                    self._set_action("idle")
                    self.frames_since_idle += 1
                else:
                    self._set_action("afk")

        #
        cur_anim = animations[self.name][self.action]
        if self.time_since_last_frame > cur_anim[self.frame]["time"]:
            self.frame += 1
            if self.frame >= len(cur_anim):
                self.frame = 0
            self.time_since_last_frame = 0
        img = cur_anim[self.frame]["img"]
        self.img = pg.transform.flip(img, self.flip, False)

    def _move_and_collide(self, velocity, collision_rects, collision_mask=None):
        collision_types = {"top": False, "bottom": False, "right": False, "left": False}

        # Horizontal (+ slopes)
        self.x += velocity[0]

        hit_list = self.rect.collidelistall(collision_rects)
        for tile_i in hit_list:
            if velocity[0] > 0:
                self.x = collision_rects[tile_i].left - self.width // 2
                collision_types["right"] = True
            elif velocity[0] < 0:
                self.x = collision_rects[tile_i].right + self.width // 2
                collision_types["left"] = True

        if self._collided_with_mask(collision_mask):
            if not self._try_sliding_slope(collision_mask):
                if velocity[0] > 0:
                    while self._collided_with_mask(collision_mask):
                        self.x -= 1
                    collision_types["right"] = True
                elif velocity[0] < 0:
                    while self._collided_with_mask(collision_mask):
                        self.x += 1
                    collision_types["left"] = True

        # Vertical
        self.y += velocity[1]

        hit_list = self.rect.collidelistall(collision_rects)
        for tile_i in hit_list:
            if velocity[1] > 0:
                self.y = collision_rects[tile_i].top - self.height // 2
                collision_types["bottom"] = True
            elif velocity[1] < 0:
                self.y = collision_rects[tile_i].bottom + self.height // 2
                collision_types["top"] = True

        if self._collided_with_mask(collision_mask):
            if velocity[1] > 0:
                while self._collided_with_mask(collision_mask):
                    self.y -= 1
                collision_types["bottom"] = True
            elif velocity[1] < 0:
                while self._collided_with_mask(collision_mask):
                    self.y += 1
                collision_types["top"] = True

        return collision_types

    def _collided_with_mask(self, collision_mask):
        if collision_mask is None:
            return False
        rect = self.rect
        return collision_mask.overlap(self.mask, (rect.x, rect.y)) is not None

    def _try_sliding_slope(self, collision_mask):
        nx, ny = self.hit_box_top_left
        for i in range(1, 4):
            temp_y = ny - i
            if collision_mask.overlap(self.mask, (nx, temp_y)) is None:
                self.y -= i
                return True
        for i in range(1, 4):
            temp_y = ny + i
            if collision_mask.overlap(self.mask, (nx, temp_y)) is None:
                self.y += i
                return True
        return False

    def get_current_mask(self):
        key = "img_mask_flip" if self.flip else "img_mask"
        return animations[self.name][self.action][self.frame][key]


def load_sprites(entities_dir):
    with open(os.path.join(entities_dir, "config.json")) as f:
        config = json.load(f)

    for entity in config.keys():
        entity_cfg = config[entity]
        entity_sprites = animations[entity] = {}

        for action in entity_cfg:
            entity_sprites[action] = []
            num_frames = len(entity_cfg[action]["timings"])

            spritesheet = pg.image.load(
                os.path.join(entities_dir, entity, f"{entity}_{action}.png")
            ).convert_alpha()
            images = SpriteSheetExtractor(spritesheet).load_strip(
                (0, 0, spritesheet.get_width() / num_frames, spritesheet.get_height()),
                image_count=num_frames,
            )

            for n, frame_time in enumerate(entity_cfg[action]["timings"]):
                entity_sprites[action].append(
                    {
                        "img": images[n],
                        "time": frame_time,
                        "img_mask": pg.mask.from_surface(images[n]),
                        "img_mask_flip": pg.mask.from_surface(
                            pg.transform.flip(images[n], True, False)
                        ),
                    }
                )
