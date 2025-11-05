from dataclasses import dataclass
from .constants import TILE_COLORS
from typing import Optional
import pygame
import math


@dataclass
class Tile:
    value: int
    row: int
    col: int
    x: float = 0.0
    y: float = 0.0
    merge_partner: Optional["Tile"] = None

    def __post_init__(self):
        self.update_pos()

    def update_pos(self):
        from .constants import RECT_WIDTH, RECT_HEIGHT

        self.x = self.col * RECT_WIDTH
        self.y = self.row * RECT_HEIGHT

    def get_color(self):
        power = int(math.log2(self.value))
        return TILE_COLORS.get(self.value, (0, 0, 0))

    def draw(self, window, font):
        from .constants import RECT_WIDTH, RECT_HEIGHT, FONT_COLOR

        color = self.get_color()
        pygame.draw.rect(window, color, (self.x, self.y, RECT_WIDTH, RECT_HEIGHT))

        if self.value > 4:
            text_color = (255, 255, 255)
        else:
            text_color = FONT_COLOR

        text = font.render(str(self.value), True, text_color)
        window.blit(
            text,
            (
                self.x + (RECT_WIDTH - text.get_width()) // 2,
                self.y + (RECT_HEIGHT - text.get_height()) // 2,
            ),
        )
