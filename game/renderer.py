import pygame
from .constants import *
from .board import Board, Animation
from .tile import Tile
from typing import List


class Renderer:
    def __init__(self, window: pygame.Surface):
        self.window = window
        self.font = pygame.font.SysFont("comicsans", 60, bold=True)

    def draw(self, board: Board):
        self.window.fill(BACKGROUND_COLOR)
        for tile in board.get_tiles():
            tile.draw(self.window, self.font)
        self._draw_grid()
        pygame.display.update()

    def animate(self, animations: List[Animation], board: Board, clock):
        if not animations:
            return

        for frame in range(ANIM_FRAMES):
            t = (frame + 1) / ANIM_FRAMES
            eased = 1 - (1 - t) ** 3  # ease out cubic

            for anim in animations:
                sx, sy = anim.start
                ex, ey = anim.end
                anim.tile.x = sx + (ex - sx) * eased
                anim.tile.y = sy + (ey - sy) * eased

            self.draw(board)
            clock.tick(FPS)

        for tile in board.get_tiles():
            tile.update_pos()

        self.draw(board)

    def _draw_grid(self):
        for row in range(1, ROWS):
            y = row * RECT_HEIGHT
            pygame.draw.line(
                self.window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS
            )

        for col in range(1, COLS):
            x = col * RECT_WIDTH
            pygame.draw.line(
                self.window, OUTLINE_COLOR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS
            )

        pygame.draw.rect(
            self.window, OUTLINE_COLOR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS
        )
