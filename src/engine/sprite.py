import json
import logging
import os

import pygame as pg

sprite_images = {}
animation_frames = {}


class SpriteSheet:
    def __init__(self, image, colorkey=None):
        self.colorkey = colorkey
        self.sheet = image

    def image_at(self, rectangle, colorkey=None):
        """Load a specific image from a specific rect."""
        rect = pg.Rect(rectangle)
        image = pg.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        ck = colorkey or self.colorkey
        if ck is None:
            image = image.convert_alpha()
        else:
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


def load_sprites(entities_dir):
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
