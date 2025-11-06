import pygame
import pytweening
from .constants import *
from .board import Board, Animation
from .tile import Tile
from typing import List


class Renderer:
    def __init__(self, window: pygame.Surface):
        self.window = window
        self.font = pygame.font.SysFont(FONT_NAME, TILE_FONT_SIZE, bold=True)
        self.score_font = pygame.font.SysFont(FONT_NAME, SCORE_FONT_SIZE, bold=True)
        self.label_font = pygame.font.SysFont(FONT_NAME, LABEL_FONT_SIZE, bold=True)

    def draw(self, board: Board, score: int = 0, best_score: int = 0):
        self.window.fill(BACKGROUND_COLOR)

        # Draw header section
        self._draw_header(score, best_score)

        # Draw tiles
        for tile in board.get_tiles():
            tile.draw(self.window, self.font)

        # Draw grid below header
        self._draw_grid()

        pygame.display.update()

    def animate(self, board: Board, clock, score: int = 0, best_score: int = 0):
        # Check if any tiles have animations
        animating_tiles = [tile for tile in board.get_tiles() if tile.has_animation()]

        if not animating_tiles:
            return

        for frame in range(ANIM_FRAMES):
            t = (frame + 1) / ANIM_FRAMES
            eased = pytweening.easeOutCubic(t)

            # Update each animating tile's position
            for tile in animating_tiles:
                tile.x = (
                    tile.anim_start_x + (tile.anim_end_x - tile.anim_start_x) * eased
                )
                tile.y = (
                    tile.anim_start_y + (tile.anim_end_y - tile.anim_start_y) * eased
                )

            # Draw all tiles (moving tiles have updated x,y)
            self.draw(board, score, best_score)
            clock.tick(FPS)

        # Animation done - clear animation state and snap to final positions
        for tile in animating_tiles:
            tile.clear_animation()

    def _draw_header(self, score: int, best_score: int):
        """Draw the header section with score and best score."""
        # Draw header background (same as main background)
        pygame.draw.rect(self.window, BACKGROUND_COLOR, (0, 0, WIDTH, HEADER_HEIGHT))

        # Score box dimensions and positioning
        box_width = 150
        box_height = 70
        box_y = (HEADER_HEIGHT - box_height) // 2
        box_spacing = 10

        # Calculate total width needed for both boxes
        total_width = box_width * 2 + box_spacing

        # Center the boxes horizontally
        start_x = (WIDTH - total_width) // 2

        # Score box (left)
        score_box_x = start_x
        pygame.draw.rect(
            self.window,
            OUTLINE_COLOR,
            (score_box_x, box_y, box_width, box_height),
            border_radius=5,
        )

        # Best score box (right)
        best_box_x = start_x + box_width + box_spacing
        pygame.draw.rect(
            self.window,
            OUTLINE_COLOR,
            (best_box_x, box_y, box_width, box_height),
            border_radius=5,
        )

        # Draw labels
        score_label = self.label_font.render("SCORE", True, (238, 228, 218))
        best_label = self.label_font.render("BEST", True, (238, 228, 218))

        self.window.blit(
            score_label,
            (score_box_x + (box_width - score_label.get_width()) // 2, box_y + 10),
        )
        self.window.blit(
            best_label,
            (best_box_x + (box_width - best_label.get_width()) // 2, box_y + 10),
        )

        # Draw scores
        score_text = self.score_font.render(str(score), True, (255, 255, 255))
        best_text = self.score_font.render(str(best_score), True, (255, 255, 255))

        self.window.blit(
            score_text,
            (score_box_x + (box_width - score_text.get_width()) // 2, box_y + 35),
        )
        self.window.blit(
            best_text,
            (best_box_x + (box_width - best_text.get_width()) // 2, box_y + 35),
        )

    def _draw_grid(self):
        """Draw the grid starting below the header."""
        # Draw vertical lines (between columns)
        for col in range(COLS + 1):
            x = col * (RECT_WIDTH + OUTLINE_THICKNESS)
            pygame.draw.rect(
                self.window,
                OUTLINE_COLOR,
                (x, GRID_TOP, OUTLINE_THICKNESS, GRID_HEIGHT),
            )

        # Draw horizontal lines (between rows) - offset by GRID_TOP
        for row in range(ROWS + 1):
            y = GRID_TOP + row * (RECT_HEIGHT + OUTLINE_THICKNESS)
            pygame.draw.rect(
                self.window, OUTLINE_COLOR, (0, y, WIDTH, OUTLINE_THICKNESS)
            )
