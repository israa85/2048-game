import pygame
from game.board import Board
from game.renderer import Renderer
from game.constants import WIDTH, HEIGHT, FPS

ANIMATING = False


def main():
    global ANIMATING
    pygame.init()

    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("2048")
    clock = pygame.time.Clock()

    board = Board()
    renderer = Renderer(window)
    score = 0
    best_score = 5036  # Placeholder

    renderer.draw(board, score, best_score)

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN and not ANIMATING:
                direction = None
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

                    moved = board.move(direction)
                    if moved:
                        renderer.animate(board, clock, score, best_score)
                        board.finalize_move()
                        board.spawn_random()
                    ANIMATING = False
                    renderer.draw(board, score, best_score)

                    if board.is_game_over():
                        print("GAME OVER")

        renderer.draw(board, score, best_score)

    pygame.quit()


if __name__ == "__main__":
    main()
