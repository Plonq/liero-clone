import json
import logging
import os

import pygame as pg
from pygame.math import Vector2

from .game import GameObject
from .utils import blit_aligned

sprite_images = {}
animation_frames = {}


class Entity(GameObject):
    def __init__(self, game, id, x=0, y=0, width=1, height=1):
        self.game = game
        self.id = id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.run_speed = 1
        self.speed_y = 0
        self.air_timer = 0
        self.jump_buffer = 6
        self.direction_x = 0
        self.action = "idle"
        self.animation_frame = 0
        self.frames_since_idle = 0
        self.flip = False
        self.img = pg.transform.flip(
            sprite_images[self.id][animation_frames[self.id][self.action][0]],
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
        self._animate()

    def draw(self, surface, offset):
        offset_rect = self.rect
        offset_rect.center = (self.x, self.y)
        offset_rect.x -= offset[0]
        offset_rect.y -= offset[1]
        blit_aligned(self.img, surface, offset_rect, h_align="center", v_align="bottom")
        # pg.draw.rect(surface, (255, 0, 0), offset_rect, 1)
        # pg.draw.rect(surface, (0, 255, 0), (self.x, self.y, 1, 1))

    def _set_action(self, action):
        if action in animation_frames[self.id]:
            if self.action != action:
                self.action = action
                self.animation_frame = 0

    def _animate(self):
        # Facing left or right?
        if self.direction_x < 0:
            self.frames_since_idle = 0
            self.flip = True
        elif self.direction_x > 0:
            self.frames_since_idle = 0
            self.flip = False

        # In the air?
        if self.air_timer > self.jump_buffer:
            if self.speed_y < 0:
                self._set_action("jump")
            elif self.speed_y > 0:
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

        # Set image based on action and current animation timer
        self.animation_frame += 1
        if self.animation_frame > len(animation_frames[self.id][self.action]) - 1:
            self.animation_frame = 0
        img_id = animation_frames[self.id][self.action][self.animation_frame]
        # TODO: Make more efficient
        self.img = pg.transform.flip(sprite_images[self.id][img_id], self.flip, False)

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


def load_animation_data(entities_dir):
    with open(os.path.join(entities_dir, "config.json")) as f:
        config = json.load(f)

    for entity in config.keys():
        entity_cfg = config[entity]
        entity_imgs = sprite_images[entity] = {}
        entity_frames = animation_frames[entity] = {}

        for action in entity_cfg:
            action_path = os.path.join(entities_dir, entity, action)

            if not os.path.exists(action_path):
                logging.warning("Action folder not found: %s", action_path)

            frame_list = []
            for n, frame_time in enumerate(entity_cfg[action]["timings"]):
                img_path = os.path.join(action_path, f"{action}_{n}.png")
                img = pg.image.load(img_path).convert_alpha()
                img_id = os.path.basename(img_path)
                entity_imgs[img_id] = img
                for i in range(frame_time):
                    frame_list.append(img_id)
            entity_frames[action] = frame_list
