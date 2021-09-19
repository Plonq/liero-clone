import pygame as pg
from src.engine.sprite import SpriteSheetExtractor

CHARACTER_ORDER = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
    ".",
    "-",
    ",",
    ":",
    "+",
    "'",
    "!",
    "?",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "(",
    ")",
    "/",
    "_",
    "=",
    "\\",
    "[",
    "]",
    "*",
    '"',
    "<",
    ">",
    ";",
]


class Font:
    def __init__(self, img):
        self.characters = {}
        self.spacing = 1
        self.font_color = pg.Color("red")
        self.height = img.get_height()
        sheet_extractor = SpriteSheetExtractor(img)
        current_char_width = 0
        character_count = 0
        for x in range(img.get_width()):
            c = img.get_at((x, 0))
            if c[0] == 127:
                char_img = sheet_extractor.image_at(
                    (
                        x - current_char_width,
                        0,
                        current_char_width,
                        self.height,
                    )
                )
                self.characters[CHARACTER_ORDER[character_count]] = char_img
                character_count += 1
                current_char_width = 0
            else:
                current_char_width += 1
        self.space_width = self.characters["A"].get_width()

    def draw(self, surface, text, color, location):
        x_offset = 0
        for char in text:
            if char != " ":
                img = self.characters[char].copy()
                pg.transform.threshold(
                    img,
                    img,
                    search_color=self.font_color,
                    threshold=0,
                    set_color=color,
                    inverse_set=True,
                )
                surface.blit(img, (location.x + x_offset, location.y))
                x_offset += self.characters[char].get_width() + self.spacing
            else:
                x_offset += self.space_width + self.spacing

    def calculate_width(self, text):
        total_width = 0
        for char in text:
            if char == " ":
                total_width += self.space_width + self.spacing
            else:
                total_width += self.characters[char].get_width() + self.spacing
        return total_width - self.spacing
