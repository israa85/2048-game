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
    # Animation tracking
    anim_start_x: Optional[float] = None
    anim_start_y: Optional[float] = None
    anim_end_x: Optional[float] = None
    anim_end_y: Optional[float] = None

    def __post_init__(self):
        # Only update pos if x and y are still at default 0.0
        if self.x == 0.0 and self.y == 0.0:
            self.update_pos()

    def update_pos(self):
        from .constants import GRID_X, GRID_Y

        self.x = GRID_X[self.col]
        self.y = GRID_Y[self.row]
    
    def set_animation(self, start_row: int, start_col: int, end_row: int, end_col: int):
        """Set up animation from start grid position to end grid position."""
        from .constants import GRID_X, GRID_Y
        self.anim_start_x = GRID_X[start_col]
        self.anim_start_y = GRID_Y[start_row]
        self.anim_end_x = GRID_X[end_col]
        self.anim_end_y = GRID_Y[end_row]
        # Set current position to start
        self.x = self.anim_start_x
        self.y = self.anim_start_y
    
    def has_animation(self) -> bool:
        return self.anim_start_x is not None
    
    def clear_animation(self):
        self.anim_start_x = None
        self.anim_start_y = None
        self.anim_end_x = None
        self.anim_end_y = None

    def get_color(self):
        power = int(math.log2(self.value))
        return TILE_COLORS.get(self.value, (0, 0, 0))

    def draw(self, window, font):
        from .constants import RECT_WIDTH, RECT_HEIGHT, FONT_COLOR, TILE_PADDING

        color = self.get_color()
        
        # Draw rect with padding (no rounded corners)
        pad = TILE_PADDING
        w = max(1, RECT_WIDTH - pad * 2)
        h = max(1, RECT_HEIGHT - pad * 2)
        rx = self.x + pad
        ry = self.y + pad
        pygame.draw.rect(window, color, (rx, ry, w, h))

        if self.value > 4:
            text_color = (255, 255, 255)
        else:
            text_color = FONT_COLOR

        text = font.render(str(self.value), True, text_color)
        window.blit(
            text,
            (
                rx + (w - text.get_width()) // 2,
                ry + (h - text.get_height()) // 2,
            ),
        )
