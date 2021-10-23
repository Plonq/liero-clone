import pygame as pg


class SpriteSheetExtractor:
    def __init__(self, image, colorkey=None):
        self.colorkey = colorkey
        self.sheet = image

    def image_at(self, rectangle, colorkey=None):
        """Load a specific image from a specific rect."""
        rect = pg.Rect(rectangle)
        if colorkey:
            image = pg.Surface(rect.size).convert()
            image.set_colorkey(colorkey)
        else:
            image = pg.Surface(rect.size).convert_alpha()
        image.blit(self.sheet, (0, 0), rect)
        return image

    def images_at(self, rects, colorkey=None):
        """Load multiple images from a list of rects."""
        ck = colorkey or self.colorkey
        return [self.image_at(rect, ck) for rect in rects]

    def load_strip(self, rect, image_count, offset=0, colorkey=None):
        """Load a strip of images and return them as a list."""
        tups = [
            (rect[0] + rect[2] * x + offset, rect[1], rect[2], rect[3])
            for x in range(image_count)
        ]
        ck = colorkey or self.colorkey
        return self.images_at(tups, ck)


class SpriteStrip:
    """Splits a spritesheet strip into separate images."""

    def __init__(self, img, start_frame=0):
        self.img = img
        total_frames = int(img.get_width() / img.get_height())
        frame_width = img.get_width() / total_frames
        self.frames = total_frames - start_frame
        start_x = start_frame * frame_width
        self.images = SpriteSheetExtractor(img).load_strip(
            (0, 0, frame_width, img.get_height()),
            image_count=self.frames,
            offset=start_x,
        )

    def get_frame(self, index=0):
        return self.images[index]
