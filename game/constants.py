import pygame

WIDTH, HEIGHT = 800, 900  # Increased height for header
FPS = 120

HEADER_HEIGHT = 100
GRID_TOP = HEADER_HEIGHT

ROWS = COLS = 4
OUTLINE_THICKNESS = 10

# Calculate cell dimensions accounting for grid lines
# Grid height = HEIGHT - HEADER_HEIGHT = 900 - 100 = 800
GRID_HEIGHT = HEIGHT - HEADER_HEIGHT
RECT_WIDTH = (WIDTH - OUTLINE_THICKNESS * (COLS + 1)) / COLS
RECT_HEIGHT = (GRID_HEIGHT - OUTLINE_THICKNESS * (ROWS + 1)) / ROWS

BACKGROUND_COLOR = (205, 192, 180)
OUTLINE_COLOR = (187, 173, 160)
FONT_COLOR = (119, 110, 101)

# Score box colors
SCORE_BOX_BG = (187, 173, 160)
SCORE_LABEL_COLOR = (238, 228, 218)
SCORE_TEXT_COLOR = (255, 255, 255)

# Button colors
BUTTON_BG = (143, 122, 102)
BUTTON_TEXT_COLOR = (255, 255, 255)
BUTTON_DISABLED_BG = (170, 160, 150)
BUTTON_DISABLED_TEXT = (200, 190, 180)

# Game over overlay styling
GAME_OVER_OVERLAY_COLOR = (0, 0, 0)  # base color, alpha applied dynamically
GAME_OVER_OVERLAY_ALPHA = 200  # final overlay alpha
GAME_OVER_PANEL_BG = (238, 228, 218)  # light tile-like panel
GAME_OVER_TITLE_COLOR = (119, 110, 101)
GAME_OVER_TEXT_COLOR = (119, 110, 101)

# YOU WIN overlay (new)
YOU_WIN_OVERLAY_COLOR = (255, 223, 0)  # yellow overlay base color
YOU_WIN_OVERLAY_ALPHA = 200  # transparency for the YOU WIN overlay
YOU_WIN_TEXT_COLOR = (255, 255, 255)  # white text for YOU WIN

# YOU WIN font sizes (new constants)
YOU_WIN_TITLE_FONT_SIZE = 72
YOU_WIN_MSG_FONT_SIZE = 24

# YOU WIN fade steps
YOU_WIN_FADE_STEPS = 12

# Keyboard key to toggle/view YOU WIN screen
YOU_WIN_KEY = pygame.K_y

# Tile colors
TILE_COLORS = {
    2: (237, 225, 218),
    4: (238, 225, 201),
    8: (243, 178, 122),
    16: (246, 150, 101),
    32: (247, 124, 95),
    64: (247, 95, 59),
    128: (237, 208, 115),
    256: (237, 204, 99),
    512: (236, 202, 80),
    1024: (0, 0, 0),
    2048: (0, 0, 0),
}

# Font settings

if pygame.font.match_font("Clear Sans"):
    FONT_NAME = "Clear Sans"
elif pygame.font.match_font("Clear Sans Medium"):
    FONT_NAME = "Clear Sans Medium"
else:
    FONT_NAME = "couriernew"

MONO_FONT_NAME = "couriernew"

TILE_FONT_SIZE = 100
TILE_FONT_SIZE_FOUR_DIGIT = 64
SCORE_FONT_SIZE = 32
LABEL_FONT_SIZE = 18
BUTTON_FONT_SIZE = 20
GAME_OVER_TITLE_FONT_SIZE = 60
GAME_OVER_MSG_FONT_SIZE = 22

# Start screen specific font sizes and dimensions
START_SCREEN_TITLE_FONT_SIZE = 100
START_SCREEN_BEST_LABEL_FONT_SIZE = 25
START_SCREEN_BEST_VALUE_FONT_SIZE = 80
START_SCREEN_INSTRUCTION_FONT_SIZE = 28
START_SCREEN_PANEL_WIDTH = 480
START_SCREEN_PANEL_HEIGHT = 390
START_SCREEN_CREDIT_FONT_SIZE = 18

# Game over screen dimensions
GAME_OVER_PANEL_WIDTH = 420
GAME_OVER_PANEL_HEIGHT = 260

# Transition and animation settings
GAME_OVER_DELAY_SECONDS = 1.5  # Delay before showing game over screen
START_FADE_PANEL_STEPS = 10  # Number of steps for panel content fade out
START_FADE_OVERLAY_STEPS = 10  # Number of steps for dark overlay fade out
START_FADE_DURATION_MS = 400  # Total duration of start fade in milliseconds

# Precomputed grid coordinates for each position (offset by GRID_TOP)
GRID_X = [OUTLINE_THICKNESS + c * (RECT_WIDTH + OUTLINE_THICKNESS) for c in range(COLS)]
GRID_Y = [
    GRID_TOP + OUTLINE_THICKNESS + r * (RECT_HEIGHT + OUTLINE_THICKNESS)
    for r in range(ROWS)
]

ANIM_FRAMES = 10
TILE_PADDING = 0

# Optional: Enable tile spawn animation (currently not implemented)
SPAWN_ANIMATION_ENABLED = False
SPAWN_ANIMATION_FRAMES = 8
