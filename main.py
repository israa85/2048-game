import pygame
from game.board import Board
from game.renderer import Renderer
from game.score_manager import ScoreManager
from game.constants import (
    WIDTH,
    HEIGHT,
    FPS,
    HEADER_HEIGHT,
    GAME_OVER_OVERLAY_ALPHA,
    GAME_OVER_DELAY_SECONDS,
    START_FADE_PANEL_STEPS,
    START_FADE_OVERLAY_STEPS,
    START_FADE_DURATION_MS,
    YOU_WIN_KEY,
    YOU_WIN_FADE_STEPS,
    YOU_WIN_OVERLAY_ALPHA,
)
from typing import Tuple, Optional
import time

# Global flag to prevent multiple moves during animation
ANIMATING: bool = False


def get_button_rects() -> Tuple[pygame.Rect, pygame.Rect]:
    """Calculate clickable rectangles for undo and reset buttons.

    Returns:
        Tuple of (undo_rect, reset_rect) for collision detection
    """
    button_width: int = 80
    button_height: int = 40
    button_y: int = (HEADER_HEIGHT - button_height) // 2
    button_spacing: int = 10
    button_left_margin: int = 20

    undo_rect: pygame.Rect = pygame.Rect(
        button_left_margin, button_y, button_width, button_height
    )
    reset_rect: pygame.Rect = pygame.Rect(
        button_left_margin + button_width + button_spacing,
        button_y,
        button_width,
        button_height,
    )

    return undo_rect, reset_rect


def fade_out_start_screen(
    renderer: Renderer,
    board: Board,
    score_manager: ScoreManager,
    window: pygame.Surface,
) -> None:
    """Perform two-stage fade: first panel content, then dark overlay.

    Args:
        renderer: The renderer instance
        board: The game board
        score_manager: Score manager for best score
        window: The pygame window surface
    """
    # Stage 1: Fade out panel content
    panel_fade_delay: int = (START_FADE_DURATION_MS // 2) // START_FADE_PANEL_STEPS
    for i in range(START_FADE_PANEL_STEPS, -1, -1):
        content_alpha: int = int(255 * i / START_FADE_PANEL_STEPS)
        renderer.draw(board, board.score, score_manager.get_best_score(), update=False)
        renderer.draw_start_screen(score_manager.get_best_score(), content_alpha)
        pygame.display.update()
        pygame.time.wait(panel_fade_delay)

    # Stage 2: Fade out dark overlay
    overlay_fade_delay: int = (START_FADE_DURATION_MS // 2) // START_FADE_OVERLAY_STEPS
    for i in range(START_FADE_OVERLAY_STEPS, -1, -1):
        overlay_alpha: int = int(120 * i / START_FADE_OVERLAY_STEPS)
        renderer.draw(board, board.score, score_manager.get_best_score(), update=False)
        if overlay_alpha > 0:
            overlay: pygame.Surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, overlay_alpha))
            window.blit(overlay, (0, 0))
        pygame.display.update()
        pygame.time.wait(overlay_fade_delay)


def fade_in_you_win(
    renderer: Renderer,
    board: Board,
    score_manager: ScoreManager,
    window: pygame.Surface,
    clock: pygame.time.Clock,
) -> None:
    """Fade the YOU WIN overlay in over multiple steps."""
    # Stage 1: fade overlay in (text hidden)
    for i in range(YOU_WIN_FADE_STEPS):
        overlay_alpha: int = int(YOU_WIN_OVERLAY_ALPHA * (i + 1) / YOU_WIN_FADE_STEPS)
        renderer.draw(board, board.score, score_manager.get_best_score(), update=False)
        renderer.draw_you_win_overlay(overlay_alpha=overlay_alpha, text_alpha=0)
        pygame.display.update()
        clock.tick(max(1, FPS // 6))

    # Stage 2: fade text in on top of final overlay
    for i in range(YOU_WIN_FADE_STEPS):
        text_alpha: int = int(255 * (i + 1) / YOU_WIN_FADE_STEPS)
        renderer.draw(board, board.score, score_manager.get_best_score(), update=False)
        # overlay at full alpha, text with increasing alpha
        renderer.draw_you_win_overlay(
            overlay_alpha=YOU_WIN_OVERLAY_ALPHA, text_alpha=text_alpha
        )
        pygame.display.update()
        clock.tick(max(1, FPS // 6))


def main() -> None:
    """Main game loop handling events, updates, and rendering."""
    global ANIMATING
    pygame.init()

    # Initialize window and clock
    window: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("2048")
    clock: pygame.time.Clock = pygame.time.Clock()

    # Initialize game components
    board: Board = Board()
    renderer: Renderer = Renderer(window)
    score_manager: ScoreManager = ScoreManager()

    # Get button collision rectangles
    undo_rect: pygame.Rect
    reset_rect: pygame.Rect
    undo_rect, reset_rect = get_button_rects()

    # Game state flags
    start_screen: bool = True  # Show start screen initially
    game_over: bool = False  # Track if game has ended
    show_you_win: bool = False  # Toggle to display YOU WIN overlay

    # Initial render: show start screen
    renderer.draw(board, board.score, score_manager.get_best_score(), update=False)
    renderer.draw_start_screen(score_manager.get_best_score())
    pygame.display.update()

    # Main game loop
    run: bool = True
    while run:
        clock.tick(FPS)

        # Process all events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            # Toggle/show YOU WIN overlay with assigned key (fade in when showing)
            if event.type == pygame.KEYDOWN and event.key == YOU_WIN_KEY:
                if not show_you_win:
                    fade_in_you_win(renderer, board, score_manager, window, clock)
                    show_you_win = True
                else:
                    # hide immediately
                    show_you_win = False
                continue

            # Handle mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN and not ANIMATING:
                mouse_pos: Tuple[int, int] = event.pos

                # If YOU WIN overlay visible, clicking anywhere keeps playing (dismiss overlay)
                if show_you_win:
                    show_you_win = False
                    # immediate redraw for responsiveness
                    renderer.draw(
                        board, board.score, score_manager.get_best_score(), update=False
                    )
                    pygame.display.update()
                    continue

                # Game over screen: click anywhere to reset (but not on reset button)
                if game_over:
                    # Only allow undo button to work, ignore reset button
                    if undo_rect.collidepoint(mouse_pos) and board.undo_available:
                        if board.undo():
                            game_over = False
                            score_manager.update_best_score(board.score)
                            renderer.draw(
                                board, board.score, score_manager.get_best_score()
                            )
                    elif not reset_rect.collidepoint(mouse_pos):
                        # Click anywhere except reset button to reset
                        board.reset()
                        game_over = False
                        renderer.draw(
                            board, board.score, score_manager.get_best_score()
                        )
                    continue

                # Start screen: click anywhere to begin game (except reset button)
                if start_screen:
                    if not reset_rect.collidepoint(mouse_pos):
                        fade_out_start_screen(renderer, board, score_manager, window)
                        start_screen = False
                    continue

                # Check undo button click (only when enabled and not in start/end screens)
                if undo_rect.collidepoint(mouse_pos) and board.undo_available:
                    if board.undo():
                        game_over = False
                        score_manager.update_best_score(board.score)
                        renderer.draw(
                            board, board.score, score_manager.get_best_score()
                        )

                # Check reset button click (only when not in start/end screens)
                elif reset_rect.collidepoint(mouse_pos):
                    board.reset()
                    game_over = False
                    renderer.draw(board, board.score, score_manager.get_best_score())

            # Handle keyboard input during active gameplay
            if (
                event.type == pygame.KEYDOWN
                and not ANIMATING
                and not game_over
                and not start_screen
            ):
                direction: Optional[str] = None
                if event.key == pygame.K_LEFT:
                    direction = "left"
                elif event.key == pygame.K_RIGHT:
                    direction = "right"
                elif event.key == pygame.K_UP:
                    direction = "up"
                elif event.key == pygame.K_DOWN:
                    direction = "down"

                if direction:
                    ANIMATING = True

                    # Attempt move in specified direction
                    moved: bool = board.move(direction)
                    if moved:
                        # Animate tiles to new positions
                        renderer.animate(
                            board, clock, board.score, score_manager.get_best_score()
                        )
                        # Finalize move (update tile values and positions)
                        board.finalize_move()
                        # Spawn new tile after successful move
                        board.spawn_random()
                        # Update high score if current score is higher
                        score_manager.update_best_score(board.score)

                    ANIMATING = False
                    renderer.draw(board, board.score, score_manager.get_best_score())

                    # Check for game over condition
                    if board.is_game_over():
                        # Pause for 1.5 seconds before showing game over
                        start_time: float = time.time()
                        while time.time() - start_time < GAME_OVER_DELAY_SECONDS:
                            clock.tick(FPS)
                            # Keep drawing to maintain responsiveness
                            renderer.draw(
                                board, board.score, score_manager.get_best_score()
                            )

                        game_over = True
                        # Fade in game over overlay smoothly
                        steps: int = 12
                        for i in range(steps):
                            renderer.draw(
                                board,
                                board.score,
                                score_manager.get_best_score(),
                                update=False,
                            )
                            alpha: int = int(GAME_OVER_OVERLAY_ALPHA * (i + 1) / steps)
                            renderer.draw_game_over_overlay(
                                board.score, score_manager.get_best_score(), alpha
                            )
                            pygame.display.update()
                            clock.tick(FPS // 2)

            # Start screen: allow keyboard to start game
            if event.type == pygame.KEYDOWN and start_screen:
                if event.key in (
                    pygame.K_LEFT,
                    pygame.K_RIGHT,
                    pygame.K_UP,
                    pygame.K_DOWN,
                    pygame.K_RETURN,
                    pygame.K_SPACE,
                ):
                    fade_out_start_screen(renderer, board, score_manager, window)
                    start_screen = False

        # Render appropriate screen based on game state
        if start_screen:
            # Show start screen with instructions
            renderer.draw(
                board, board.score, score_manager.get_best_score(), update=False
            )
            renderer.draw_start_screen(score_manager.get_best_score())
        elif game_over:
            # Show game over overlay with final scores
            renderer.draw(
                board, board.score, score_manager.get_best_score(), update=False
            )
            renderer.draw_game_over_overlay(board.score, score_manager.get_best_score())
        else:
            # Normal gameplay rendering
            renderer.draw(
                board, board.score, score_manager.get_best_score(), update=False
            )

        # If YOU WIN overlay is toggled on, draw it on top of whatever is shown
        if show_you_win:
            renderer.draw_you_win_overlay()

        # Single present call per frame
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
