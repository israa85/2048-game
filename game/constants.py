WIDTH, HEIGHT = 800, 900  # Increased height for header
FPS = 60

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
FONT_NAME = "couriernew"
TILE_FONT_SIZE = 100
SCORE_FONT_SIZE = 32
LABEL_FONT_SIZE = 18

ANIM_FRAMES = 5
TILE_PADDING = (
    0  # Increase this value to shrink tiles (creates more space between them)
)

# Precomputed grid coordinates for each position (offset by GRID_TOP)
GRID_X = [OUTLINE_THICKNESS + c * (RECT_WIDTH + OUTLINE_THICKNESS) for c in range(COLS)]
GRID_Y = [
    GRID_TOP + OUTLINE_THICKNESS + r * (RECT_HEIGHT + OUTLINE_THICKNESS)
    for r in range(ROWS)
]
