import pygame
import pytweening
from .constants import *
from .board import Board, Animation
from .tile import Tile
from typing import List


class Renderer:
    """Handles all visual rendering for the 2048 game including board, tiles, and overlays."""

    def __init__(self, window: pygame.Surface) -> None:
        """Initialize renderer with fonts for different UI elements.

        Args:
            window: The pygame surface to render onto
        """
        self.window: pygame.Surface = window
        # Font for tile numbers
        self.font: pygame.font.Font = pygame.font.SysFont(FONT_NAME, TILE_FONT_SIZE)
        # Font for 4-digit tile numbers (smaller)
        self.font_4digit: pygame.font.Font = pygame.font.SysFont(
            FONT_NAME, TILE_FONT_SIZE_FOUR_DIGIT
        )
        # Font for score values in header
        self.score_font: pygame.font.Font = pygame.font.SysFont(
            FONT_NAME, SCORE_FONT_SIZE
        )
        # Font for score/best labels
        self.label_font: pygame.font.Font = pygame.font.SysFont(
            FONT_NAME, LABEL_FONT_SIZE
        )
        # Font for button text
        self.button_font: pygame.font.Font = pygame.font.SysFont(
            FONT_NAME, BUTTON_FONT_SIZE
        )
        # Font for game over title
        self.go_title_font: pygame.font.Font = pygame.font.SysFont(
            FONT_NAME, GAME_OVER_TITLE_FONT_SIZE
        )
        # Font for overlay messages
        self.go_msg_font: pygame.font.Font = pygame.font.SysFont(
            FONT_NAME, GAME_OVER_MSG_FONT_SIZE
        )
        # Font for start screen title
        self.start_title_font: pygame.font.Font = pygame.font.SysFont(
            FONT_NAME, START_SCREEN_TITLE_FONT_SIZE
        )

        # YOU WIN fonts (new)
        self.you_win_title_font: pygame.font.Font = pygame.font.SysFont(
            FONT_NAME, YOU_WIN_TITLE_FONT_SIZE
        )
        self.you_win_msg_font: pygame.font.Font = pygame.font.SysFont(
            FONT_NAME, YOU_WIN_MSG_FONT_SIZE
        )

    def draw(
        self, board: Board, score: int = 0, best_score: int = 0, update: bool = True
    ) -> None:
        """Draw the complete game state including header, grid, and tiles.

        Args:
            board: The game board containing tile data
            score: Current player score
            best_score: Highest score achieved
            update: Whether to call pygame.display.update() after drawing
        """
        self.window.fill(BACKGROUND_COLOR)

        # Draw header section with scores and buttons
        self._draw_header(score, best_score, board.undo_available)

        # Draw grid lines (behind tiles so tiles appear on top)
        self._draw_grid()

        # Draw all active tiles on top of grid
        for tile in board.get_tiles():
            tile.draw(self.window, self.font, self.font_4digit)

        # NOTE: do not call pygame.display.update() here — present/update should be controlled by the main loop

    def animate(
        self,
        board: Board,
        clock: pygame.time.Clock,
        score: int = 0,
        best_score: int = 0,
    ) -> None:
        """Animate tiles moving to their new positions with easing.

        Args:
            board: The game board with tiles to animate
            clock: Pygame clock for frame timing
            score: Current score to display during animation
            best_score: Best score to display during animation
        """
        # Get all tiles that have animation data set
        animating_tiles: List[Tile] = [
            tile for tile in board.get_tiles() if tile.has_animation()
        ]

        if not animating_tiles:
            return

        # Animate over ANIM_FRAMES frames
        for frame in range(ANIM_FRAMES):
            # Calculate progress (0.0 to 1.0)
            t: float = (frame + 1) / ANIM_FRAMES
            # Apply easing function for smooth animation
            eased: float = pytweening.easeOutCubic(t)

            # Update position of each animating tile based on eased progress
            for tile in animating_tiles:
                tile.x = (
                    tile.anim_start_x + (tile.anim_end_x - tile.anim_start_x) * eased
                )
                tile.y = (
                    tile.anim_start_y + (tile.anim_end_y - tile.anim_start_y) * eased
                )

            # Redraw scene with updated tile positions
            self.draw(board, score, best_score, update=False)
            pygame.display.update()  # explicit single update per animation frame
            clock.tick(FPS)

        # Animation complete - clear animation state from all tiles
        for tile in animating_tiles:
            tile.clear_animation()

    def _draw_header(
        self, score: int, best_score: int, undo_available: bool = False
    ) -> None:
        """Draw the header bar with score displays and action buttons.

        Args:
            score: Current game score
            best_score: Highest score achieved
            undo_available: Whether the undo button should be enabled
        """
        # Draw header background
        pygame.draw.rect(self.window, BACKGROUND_COLOR, (0, 0, WIDTH, HEADER_HEIGHT))

        # Score box dimensions
        box_width: int = 150
        box_height: int = 70
        box_y: int = (HEADER_HEIGHT - box_height) // 2
        box_spacing: int = 10

        # Calculate horizontal centering for both score boxes
        total_width: int = box_width * 2 + box_spacing
        start_x: int = (WIDTH - total_width) // 2

        # Draw score box (left)
        score_box_x: int = start_x
        pygame.draw.rect(
            self.window,
            SCORE_BOX_BG,
            (score_box_x, box_y, box_width, box_height),
            border_radius=5,
        )

        # Draw best score box (right)
        best_box_x: int = start_x + box_width + box_spacing
        pygame.draw.rect(
            self.window,
            SCORE_BOX_BG,
            (best_box_x, box_y, box_width, box_height),
            border_radius=5,
        )

        # Render and position "SCORE" and "BEST" labels
        score_label: pygame.Surface = self.label_font.render(
            "SCORE", True, SCORE_LABEL_COLOR
        )
        best_label: pygame.Surface = self.label_font.render(
            "BEST", True, SCORE_LABEL_COLOR
        )

        self.window.blit(
            score_label,
            (score_box_x + (box_width - score_label.get_width()) // 2, box_y + 4),
        )
        self.window.blit(
            best_label,
            (best_box_x + (box_width - best_label.get_width()) // 2, box_y + 4),
        )

        # Render and position score values
        score_text: pygame.Surface = self.score_font.render(
            str(score), True, SCORE_TEXT_COLOR
        )
        best_text: pygame.Surface = self.score_font.render(
            str(best_score), True, SCORE_TEXT_COLOR
        )

        self.window.blit(
            score_text,
            (score_box_x + (box_width - score_text.get_width()) // 2, box_y + 22),
        )
        self.window.blit(
            best_text,
            (best_box_x + (box_width - best_text.get_width()) // 2, box_y + 22),
        )

        # Button dimensions and positioning (left side of header)
        button_width: int = 80
        button_height: int = 40
        button_y: int = (HEADER_HEIGHT - button_height) // 2
        button_spacing: int = 10
        button_left_margin: int = 20

        # Draw undo button with conditional styling based on availability
        undo_x: int = button_left_margin
        undo_bg: tuple = BUTTON_BG if undo_available else BUTTON_DISABLED_BG
        undo_text_color: tuple = (
            BUTTON_TEXT_COLOR if undo_available else BUTTON_DISABLED_TEXT
        )

        pygame.draw.rect(
            self.window,
            undo_bg,
            (undo_x, button_y, button_width, button_height),
            border_radius=5,
        )
        undo_text: pygame.Surface = self.button_font.render(
            "UNDO", True, undo_text_color
        )
        self.window.blit(
            undo_text,
            (
                undo_x + (button_width - undo_text.get_width()) // 2,
                button_y + (button_height - undo_text.get_height()) // 2,
            ),
        )

        # Draw reset button (always enabled)
        reset_x: int = undo_x + button_width + button_spacing
        pygame.draw.rect(
            self.window,
            BUTTON_BG,
            (reset_x, button_y, button_width, button_height),
            border_radius=5,
        )
        reset_text: pygame.Surface = self.button_font.render(
            "RESET", True, BUTTON_TEXT_COLOR
        )
        self.window.blit(
            reset_text,
            (
                reset_x + (button_width - reset_text.get_width()) // 2,
                button_y + (button_height - reset_text.get_height()) // 2,
            ),
        )

    def _draw_grid(self) -> None:
        """Draw the game grid lines below the header."""
        # Draw vertical lines (between and around columns)
        for col in range(COLS + 1):
            x: int = col * (RECT_WIDTH + OUTLINE_THICKNESS)
            pygame.draw.rect(
                self.window,
                OUTLINE_COLOR,
                (x, GRID_TOP, OUTLINE_THICKNESS, GRID_HEIGHT),
            )

        # Draw horizontal lines (between and around rows), offset by header
        for row in range(ROWS + 1):
            y: int = GRID_TOP + row * (RECT_HEIGHT + OUTLINE_THICKNESS)
            pygame.draw.rect(
                self.window, OUTLINE_COLOR, (0, y, WIDTH, OUTLINE_THICKNESS)
            )

    def _wrap_text(
        self, font: pygame.font.Font, text: str, max_width: int
    ) -> List[str]:
        """Wrap text into multiple lines that fit within max_width.

        Args:
            font: Font to use for measuring text width
            text: Text string to wrap
            max_width: Maximum pixel width for each line

        Returns:
            List of text lines that fit within max_width
        """
        words: List[str] = text.split(" ")
        lines: List[str] = []
        current: str = ""

        for word in words:
            # Try adding this word to current line
            test_line: str = (current + " " + word) if current else word
            if font.size(test_line)[0] <= max_width:
                current = test_line
            else:
                # Word doesn't fit, start new line
                if current:
                    lines.append(current)
                current = word

        # Add final line
        if current:
            lines.append(current)
        return lines

    def draw_start_screen(self, best_score: int, content_alpha: int = 255) -> None:
        """Draw the initial start screen overlay with game title and best score.

        Args:
            best_score: Highest score achieved to display
            content_alpha: Alpha transparency for panel content (0-255)
        """
        # Create semi-transparent dark overlay
        overlay: pygame.Surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.window.blit(overlay, (0, 0))

        # Fixed panel dimensions and position
        panel_width: int = START_SCREEN_PANEL_WIDTH
        panel_height: int = START_SCREEN_PANEL_HEIGHT
        panel_x: int = (WIDTH - panel_width) // 2  # Center horizontally
        panel_y: int = (HEIGHT - panel_height) // 2  # Center vertically

        # Draw panel background with alpha
        panel_surface: pygame.Surface = pygame.Surface(
            (panel_width, panel_height), pygame.SRCALPHA
        )
        panel_color: tuple = (*GAME_OVER_PANEL_BG, content_alpha)
        pygame.draw.rect(
            panel_surface,
            panel_color,
            (0, 0, panel_width, panel_height),
            border_radius=12,
        )
        self.window.blit(panel_surface, (panel_x, panel_y))

        # Only draw content if alpha is above threshold
        if content_alpha > 10:
            # Create fonts for start screen
            best_label_font: pygame.font.Font = pygame.font.SysFont(
                FONT_NAME, START_SCREEN_BEST_LABEL_FONT_SIZE
            )
            best_value_font: pygame.font.Font = pygame.font.SysFont(
                FONT_NAME, START_SCREEN_BEST_VALUE_FONT_SIZE
            )
            instruction_font: pygame.font.Font = pygame.font.SysFont(
                FONT_NAME, START_SCREEN_INSTRUCTION_FONT_SIZE
            )
            credit_font: pygame.font.Font = pygame.font.SysFont(
                MONO_FONT_NAME, START_SCREEN_CREDIT_FONT_SIZE, bold=True
            )

            # Calculate text color with alpha
            text_color: tuple = (*GAME_OVER_TITLE_COLOR, content_alpha)
            text_color_alt: tuple = (*GAME_OVER_TEXT_COLOR, content_alpha)

            # Draw "2048" title - fixed position
            title_surface: pygame.Surface = pygame.Surface(
                (panel_width, 120), pygame.SRCALPHA
            )
            title: pygame.Surface = self.start_title_font.render(
                "2048", True, text_color
            )
            title_surface.blit(title, ((panel_width - title.get_width()) // 2, 0))
            self.window.blit(title_surface, (panel_x, panel_y))

            # Draw "BEST" label - fixed position
            best_label: pygame.Surface = best_label_font.render(
                "BEST", True, text_color_alt
            )
            self.window.blit(
                best_label,
                (panel_x + (panel_width - best_label.get_width()) // 2, panel_y + 120),
            )

            # Draw best score value - fixed position
            best_value: pygame.Surface = best_value_font.render(
                str(best_score), True, text_color_alt
            )
            self.window.blit(
                best_value,
                (panel_x + (panel_width - best_value.get_width()) // 2, panel_y + 135),
            )

            # Draw instruction text - fixed position
            instruction_text: pygame.Surface = instruction_font.render(
                "CLICK ANYWHERE TO START", True, text_color_alt
            )
            self.window.blit(
                instruction_text,
                (
                    panel_x + (panel_width - instruction_text.get_width()) // 2,
                    panel_y + 240,
                ),
            )

            # Draw authors names and credits to original creators
            credit_text_line1: pygame.Surface = credit_font.render(
                "ARWA HAMMAD, SARA ABDEL-JAWAD", True, text_color_alt
            )

            credit_text_line2: pygame.Surface = credit_font.render(
                "OLIVIA LEE, YASHITHA TIPPANUR VENKATA", True, text_color_alt
            )

            credit_text_line3: pygame.Surface = credit_font.render(
                "ORIGINAL 2048 BY GABRIELE CIRULLI", True, text_color_alt
            )

            self.window.blit(
                credit_text_line1,
                (
                    panel_x + (panel_width - credit_text_line1.get_width()) // 2,
                    panel_y + 295,
                ),
            )

            self.window.blit(
                credit_text_line2,
                (
                    panel_x + (panel_width - credit_text_line2.get_width()) // 2,
                    panel_y + 320,
                ),
            )

            self.window.blit(
                credit_text_line3,
                (
                    panel_x + (panel_width - credit_text_line3.get_width()) // 2,
                    panel_y + 355,
                ),
            )

    def draw_game_over_overlay(
        self, score: int, best_score: int, alpha: int = GAME_OVER_OVERLAY_ALPHA
    ) -> None:
        """Draw the game over overlay with final scores and reset prompt.

        Args:
            score: Final score achieved in this game
            best_score: Highest score ever achieved
            alpha: Transparency level for the dark overlay (0-255)
        """
        # Create translucent dark overlay
        overlay: pygame.Surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        clr: tuple = (*GAME_OVER_OVERLAY_COLOR, max(0, min(255, alpha)))
        overlay.fill(clr)
        self.window.blit(overlay, (0, 0))

        # Use constants for panel dimensions and centering
        panel_width: int = GAME_OVER_PANEL_WIDTH
        panel_height: int = GAME_OVER_PANEL_HEIGHT
        panel_x: int = (WIDTH - panel_width) // 2
        panel_y: int = (HEIGHT - panel_height) // 2

        # Draw panel background
        pygame.draw.rect(
            self.window,
            GAME_OVER_PANEL_BG,
            (panel_x, panel_y, panel_width, panel_height),
            border_radius=12,
        )

        # Draw "GAME OVER" title - fixed position
        title: pygame.Surface = self.go_title_font.render(
            "GAME OVER", True, GAME_OVER_TITLE_COLOR
        )
        self.window.blit(  # GAME OVER
            title, (panel_x + (panel_width - title.get_width()) // 2, panel_y + 22)
        )

        # Render score labels and values
        score_label: pygame.Surface = self.label_font.render(
            "SCORE", True, GAME_OVER_TEXT_COLOR
        )
        score_value: pygame.Surface = self.score_font.render(
            str(score), True, GAME_OVER_TEXT_COLOR
        )
        best_label: pygame.Surface = self.label_font.render(
            "BEST", True, GAME_OVER_TEXT_COLOR
        )
        best_value: pygame.Surface = self.score_font.render(
            str(best_score), True, GAME_OVER_TEXT_COLOR
        )

        # Fixed column centers for left (score) and right (best) sections
        left_center_x: int = panel_x + panel_width // 4
        right_center_x: int = panel_x + (panel_width * 3) // 4

        # Draw left column (current score) - fixed positions
        self.window.blit(  # SCORE LABEL
            score_label, (left_center_x - score_label.get_width() // 2, panel_y + 110)
        )
        self.window.blit(  # SCORE VALUE
            score_value, (left_center_x - score_value.get_width() // 2, panel_y + 130)
        )

        # Draw right column (best score) - fixed positions
        self.window.blit(  # BEST LABEL
            best_label, (right_center_x - best_label.get_width() // 2, panel_y + 110)
        )
        self.window.blit(  # BEST VALUE
            best_value, (right_center_x - best_value.get_width() // 2, panel_y + 130)
        )

        # Draw reset instruction message - fixed position
        instruction_font: pygame.font.Font = pygame.font.SysFont(
            FONT_NAME, GAME_OVER_MSG_FONT_SIZE
        )
        instruction_text: pygame.Surface = instruction_font.render(
            "CLICK ANYWHERE TO RESET", True, GAME_OVER_TEXT_COLOR
        )
        self.window.blit(  # CLICK ANYWHERE TO RESET
            instruction_text,
            (
                panel_x + (panel_width - instruction_text.get_width()) // 2,
                panel_y + 205,
            ),
        )

    def draw_you_win_overlay(
        self,
        title: str = "YOU WIN",
        subtitle: str = "YOU MADE 2048!",
        overlay_alpha: int = YOU_WIN_OVERLAY_ALPHA,
        text_alpha: int = 255,
    ) -> None:
        """Draw a yellow YOU WIN overlay with white text.

        Args:
            title: Main title text
            subtitle: Secondary instruction text
            overlay_alpha: Overlay alpha (0-255)
            text_alpha: Text alpha (0-255)
        """
        # Full-screen translucent yellow overlay
        overlay: pygame.Surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        clr: tuple = (*YOU_WIN_OVERLAY_COLOR, max(0, min(255, overlay_alpha)))
        overlay.fill(clr)
        self.window.blit(overlay, (0, 0))

        # Title text (large)
        title_surface: pygame.Surface = self.you_win_title_font.render(
            title, True, YOU_WIN_TEXT_COLOR
        )
        title_x = (WIDTH - title_surface.get_width()) // 2
        title_y = (HEIGHT // 2) - title_surface.get_height() - 10
        # apply text alpha if provided
        if 0 <= text_alpha < 255:
            title_surface = title_surface.convert_alpha()
            title_surface.set_alpha(text_alpha)
        self.window.blit(title_surface, (title_x, title_y))

        # Subtitle / instruction (smaller)
        subtitle_surface: pygame.Surface = self.you_win_msg_font.render(
            subtitle, True, YOU_WIN_TEXT_COLOR
        )
        subtitle_x = (WIDTH - subtitle_surface.get_width()) // 2
        subtitle_y = title_y + title_surface.get_height() + 12
        if 0 <= text_alpha < 255:
            subtitle_surface = subtitle_surface.convert_alpha()
            subtitle_surface.set_alpha(text_alpha)
        self.window.blit(subtitle_surface, (subtitle_x, subtitle_y))

        # Click-to-keep-playing prompt (new)
        keep_playing_surface: pygame.Surface = self.you_win_msg_font.render(
            "CLICK TO KEEP PLAYING", True, YOU_WIN_TEXT_COLOR
        )
        kp_x = (WIDTH - keep_playing_surface.get_width()) // 2
        kp_y = subtitle_y + subtitle_surface.get_height() + 10
        if 0 <= text_alpha < 255:
            keep_playing_surface = keep_playing_surface.convert_alpha()
            keep_playing_surface.set_alpha(text_alpha)
        self.window.blit(keep_playing_surface, (kp_x, kp_y))
