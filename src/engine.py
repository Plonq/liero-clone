import json
import os

import pygame as pg

import logging

from pygame import K_SPACE, K_a, K_d

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
                img = pg.image.load(img_path)
                img_id = os.path.basename(img_path)
                entity_imgs[img_id] = img
                for i in range(frame_time):
                    frame_list.append(img_id)
            entity_frames[action] = frame_list


class Entity(object):
    def __init__(self, id, x=0, y=0, width=1, height=1):
        self.id = id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.run_speed = 1
        self.momentum_y = 0
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
        x, y = self.adjusted_pos
        return pg.Rect(x, y, self.width, self.height)

    @property
    def adjusted_pos(self):
        return int(self.x), int(self.y)
        x = self.x - (self.width // 2)
        y = self.y - (self.height // 2)
        return int(x), int(y)

    @property
    def inverse_adjusted_pos(self):
        return int(-self.x), int(-self.y)
        x = self.x - (self.width // 2)
        y = self.y - (self.height // 2)
        return int(-x), int(-y)

    def update(self, boundary_rects, collision_mask):
        self._animate()

        self.direction_x = self._get_direction()
        velocity = [0, 0]
        velocity[0] += self.direction_x * self.run_speed
        velocity[1] += self.momentum_y
        self.momentum_y += 0.3
        if self.momentum_y > 4:
            self.momentum_y = 4
        collision_directions = self._move_and_collide(
            velocity, boundary_rects, collision_mask
        )
        if collision_directions["bottom"]:
            self.momentum_y = 0
            self.air_timer = 0
        else:
            self.air_timer += 1
        if collision_directions["top"]:
            self.momentum_y = 0

    def draw(self, screen, offset=(0, 0)):
        offset_rect = self.rect.copy()
        offset_rect.x -= offset[0]
        offset_rect.y -= offset[1]
        screen.blit(self.img, offset_rect)
        # pg.draw.rect(screen, (255, 0, 0), offset_rect)

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
            if self.momentum_y < 0:
                self._set_action("jump")
            elif self.momentum_y > 0:
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

    def _get_direction(self):
        direction = 0
        key = pg.key.get_pressed()
        # Jumping
        if key[K_SPACE]:
            if self.air_timer < self.jump_buffer:
                self.momentum_y = -5
        # Move right
        if key[K_d]:
            direction += 1
        # Move left
        if key[K_a]:
            direction -= 1
        return direction

    def _move_and_collide(self, velocity, boundary_rects, collision_mask):
        collision_types = {"top": False, "bottom": False, "right": False, "left": False}

        # Horizontal
        self.x += velocity[0]

        def stop_going_right():
            overlap = self.mask.overlap(collision_mask, self.inverse_adjusted_pos)
            while overlap is not None:
                self.x -= 1
                overlap = self.mask.overlap(collision_mask, self.inverse_adjusted_pos)

        def stop_going_left():
            overlap = self.mask.overlap(collision_mask, self.inverse_adjusted_pos)
            while overlap is not None:
                self.x += 1
                overlap = self.mask.overlap(collision_mask, self.inverse_adjusted_pos)

        def try_sliding_slope():
            nx, ny = self.adjusted_pos
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

        hit_list = self.rect.collidelistall(boundary_rects)
        for tile_i in hit_list:
            if velocity[0] > 0:
                self.x = boundary_rects[tile_i].left - self.width  # // 2
                collision_types["right"] = True
            elif velocity[0] < 0:
                self.x = boundary_rects[tile_i].right  # + self.width // 2
                collision_types["left"] = True

        overlap = self.mask.overlap(collision_mask, self.inverse_adjusted_pos)
        if overlap is not None:
            if velocity[0] > 0:
                if not try_sliding_slope():
                    stop_going_right()
                    collision_types["right"] = True
            elif velocity[0] < 0:
                if not try_sliding_slope():
                    stop_going_left()
                    collision_types["left"] = True

        # Vertical
        self.y += velocity[1]

        hit_list = self.rect.collidelistall(boundary_rects)
        for tile_i in hit_list:
            if velocity[1] > 0:
                self.y = boundary_rects[tile_i].top - self.height  # // 2
                collision_types["bottom"] = True
            elif velocity[1] < 0:
                self.y = boundary_rects[tile_i].bottom  # + self.height // 2
                collision_types["top"] = True

        overlap = self.mask.overlap(collision_mask, self.inverse_adjusted_pos)
        if overlap is not None:
            if velocity[1] > 0:
                modifier = 1
                if overlap[1] < self.height // 2:
                    modifier = -1
                while overlap is not None:
                    self.y -= 1 * modifier
                    overlap = self.mask.overlap(
                        collision_mask, self.inverse_adjusted_pos
                    )
                collision_types["bottom"] = True
            elif velocity[1] < 0:
                modifier = 1
                if overlap[1] > self.height // 2:
                    modifier = -1
                while overlap is not None:
                    self.y += 1 * modifier
                    overlap = self.mask.overlap(
                        collision_mask, self.inverse_adjusted_pos
                    )
                collision_types["top"] = True

        return collision_types

    def _calculate_x_collision_type(self, overlap_mask, vel_x):
        types = {
            "left_top_slope": False,
            "left_wall": False,
            "left_bottom_slope": False,
            "right_top_slope": False,
            "right_wall": False,
            "right_bottom_slope": False,
        }
        if vel_x > 0:
            # Find all overlapping points on the right side
            size = overlap_mask.get_size()
            for x in range(size[0] - vel_x, self.width):
                for y in range(size[1]):
                    bit = overlap_mask.get_at((x, y))
                    if bit == 1:
                        if y <= 2:
                            types["right_top_slope"] = True
                        elif y >= size[1] - 3:
                            types["right_bottom_slope"] = True
                        else:
                            types["right_wall"] = True
            if types["right_top_slope"] and types["right_bottom_slope"]:
                types["right_wall"] = True
        if vel_x < 0:
            # Find all overlapping points on the left side
            size = overlap_mask.get_size()
            for x in range(0, abs(vel_x)):
                for y in range(size[1]):
                    bit = overlap_mask.get_at((x, y))
                    if bit == 1:
                        if y <= 2:
                            types["left_top_slope"] = True
                        elif y >= size[1] - 3:
                            types["left_bottom_slope"] = True
                        else:
                            types["left_wall"] = True
            if types["left_top_slope"] and types["left_bottom_slope"]:
                types["left_wall"] = True
        return types


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
