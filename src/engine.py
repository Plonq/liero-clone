import json
import os

import pygame as pg

import logging

from pygame.math import Vector2

sprite_images = {}
animation_frames = {}


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


class Entity:
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
        self.img = None
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


class SpriteSheet(object):
    def __init__(self, filename, colorkey=None):
        self.colorkey = colorkey
        try:
            self.sheet = pg.image.load(filename).convert()
        except pg.error as message:
            print("Unable to load sprite sheet image:", filename)
            raise SystemExit(message)

    def image_at(self, rectangle, colorkey=None):
        """Load a specific image from a specific rect."""
        rect = pg.Rect(rectangle)
        image = pg.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        ck = colorkey or self.colorkey
        if ck is not None:
            if ck == -1:
                ck = image.get_at((0, 0))
            image.set_colorkey(ck, pg.RLEACCEL)
        return image

    def images_at(self, rects, colorkey=None):
        """Load multiple images from a list of rects."""
        ck = colorkey or self.colorkey
        return [self.image_at(rect, ck) for rect in rects]

    def load_strip(self, rect, image_count, colorkey=None):
        """Load a strip of images and return them as a list."""
        tups = [
            (rect[0] + rect[2] * x, rect[1], rect[2], rect[3])
            for x in range(image_count)
        ]
        ck = colorkey or self.colorkey
        return self.images_at(tups, ck)


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
