import pygame
import random
import math


pygame.init()
FPS = 60

WIDTH, HEIGHT = 800, 800
ROWS = 4
COLS = 4

RECT_HEIGHT = HEIGHT//ROWS
RECT_WIDTH = WIDTH // COLS

OUTLINE_COLOR = (187, 173, 160)
OUTLINE_THICKNESS =10
BACKGROUND_COLOUR = (205, 192, 180)
FONT_COLOR = (119, 110, 101)

FONT = pygame.font.SysFont("comicsans", 60, bold=True)
MOVE_VEL = 100
ANIM_FRAMES = 10
ANIMATING = False

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")


class Tile:
    COLORS = [
        (237, 225,218),
        (238, 225, 201),
        (243, 178, 122),
        (246, 150, 101),
        (247, 124, 95),
        (247, 95, 59),
        (237, 208, 115),
        (237, 204, 99),
        (236, 202, 80),
    ]


    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.x = col * RECT_WIDTH
        self.y = row * RECT_HEIGHT
    def get_color(self):
        color_index = int(math.log2(self.value)) - 1
        color = self.COLORS[color_index]
        return color

    def draw(self, window):
        color = self.get_color()
        pygame.draw.rect(window, color, (self.x, self.y, RECT_WIDTH, RECT_HEIGHT))

        text = FONT.render(str(self.value), 1, FONT_COLOR)
        window.blit(
            text,
            (
                self.x + (RECT_WIDTH / 2 - text.get_width() / 2),
                self.y + (RECT_HEIGHT / 2 - text.get_height() / 2),
            )
        )

    def set_pos(self, ceil=False):
        if ceil:
            self.row = math.ceil(self.y / RECT_HEIGHT)
            self.col = math.ceil(self.x / RECT_WIDTH)
        else:
            self.row = math.floor(self.y / RECT_HEIGHT)
            self.col = math.floor(self.x / RECT_WIDTH)

    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]

    def set_xy_from_grid(self): # the tiles like to stray a bit during animation
        """Helper to snap x,y to current row/col positions."""
        self.x = self.col * RECT_WIDTH
        self.y = self.row * RECT_HEIGHT     

def draw_grid(window):
    for row in range(1, ROWS):
        y = row * RECT_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)

    for col in range(1, COLS):
        x = col * RECT_WIDTH
        pygame.draw.line(window, OUTLINE_COLOR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)


    pygame.draw.rect(window, OUTLINE_COLOR, (0,0, WIDTH, HEIGHT), OUTLINE_THICKNESS)


def draw(window, tiles):
    window.fill(BACKGROUND_COLOUR)

    for tile in tiles.values():
        tile.draw(window)

    draw_grid(window)

    pygame.display.update()


def get_random_pos(tiles):
    row = None
    col = None
    while True:
        row = random.randrange(0, ROWS)
        col = random.randrange(0, COLS)

        if f"{row}{col}" not in tiles:
            break

    return row,col

def move_tiles(window, tiles, clock, direction):
    global ANIMATING
    # Compute new grid positions and animations, then animate with easing.
    # Build a 2D grid of tiles (references) for easier processing.
    grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
    for t in tiles.values():
        grid[t.row][t.col] = t

    animations = []  # list of dicts: {tile, start, end, is_merge_source, merge_target_key}
    new_tiles = {}

    def handle_line(get_tile_in_line, set_new_pos):
        # get_tile_in_line(i) -> Tile or None, set_new_pos(tile, dest_index, is_merged=False, merged_with=None)
        line = []
        for i in range(4):
            tile = get_tile_in_line(i)
            if tile:
                line.append(tile)

        target_idx = 0
        i = 0
        while i < len(line):
            tile = line[i]
            if i + 1 < len(line) and line[i + 1].value == tile.value:
                # merge tile and next
                other = line[i + 1]
                # both tiles animate to same target cell
                set_new_pos(tile, target_idx, is_merged=True, merged_with=other)
                set_new_pos(other, target_idx, is_merged=True, merged_with=tile)
                target_idx += 1
                i += 2
            else:
                set_new_pos(tile, target_idx, is_merged=False, merged_with=None)
                target_idx += 1
                i += 1

    # Helpers for each direction
    if direction == "left":
        def get_tile(r, c): return grid[r][c]
        for r in range(ROWS):
            def getter(i, row=r): return get_tile(row, i)
            def setter(tile, dest_c, is_merged, merged_with, row=r):
                start = (tile.x, tile.y)
                end = (dest_c * RECT_WIDTH, row * RECT_HEIGHT)
                animations.append({"tile": tile, "start": start, "end": end, "is_merged": is_merged, "merged_with": merged_with, "dest_key": f"{row}{dest_c}"})
                # record placeholder in new_tiles; finalization after animation
            handle_line(getter, setter)
    elif direction == "right":
        def get_tile(r, c): return grid[r][c]
        for r in range(ROWS):
            def getter(i, row=r): return get_tile(row, COLS - 1 - i)
            def setter(tile, dest_i, is_merged, merged_with, row=r):
                dest_c = COLS - 1 - dest_i
                start = (tile.x, tile.y)
                end = (dest_c * RECT_WIDTH, row * RECT_HEIGHT)
                animations.append({"tile": tile, "start": start, "end": end, "is_merged": is_merged, "merged_with": merged_with, "dest_key": f"{row}{dest_c}"})
            handle_line(getter, setter)
    elif direction == "up":
        def get_tile(r, c): return grid[r][c]
        for c in range(COLS):
            def getter(i, col=c): return get_tile(i, col)
            def setter(tile, dest_r, is_merged, merged_with, col=c):
                start = (tile.x, tile.y)
                end = (col * RECT_WIDTH, dest_r * RECT_HEIGHT)
                animations.append({"tile": tile, "start": start, "end": end, "is_merged": is_merged, "merged_with": merged_with, "dest_key": f"{dest_r}{col}"})
            handle_line(getter, setter)
    elif direction == "down":
        def get_tile(r, c): return grid[r][c]
        for c in range(COLS):
            def getter(i, col=c): return get_tile(ROWS - 1 - i, col)
            def setter(tile, dest_i, is_merged, merged_with, col=c):
                dest_r = ROWS - 1 - dest_i
                start = (tile.x, tile.y)
                end = (col * RECT_WIDTH, dest_r * RECT_HEIGHT)
                animations.append({"tile": tile, "start": start, "end": end, "is_merged": is_merged, "merged_with": merged_with, "dest_key": f"{dest_r}{col}"})
            handle_line(getter, setter)

    # If no animations (no tiles moved), return without adding a new tile
    if not animations:
        return None

    # mark as animating so main loop can ignore input
    ANIMATING = True

    # Run animation frames
    frames = ANIM_FRAMES
    for f in range(frames):
        clock.tick(FPS)
        t = (f + 1) / frames
        eased = 1 - pow(1 - t, 3)  # ease-out-cubic

        # update tile positions according to eased progress
        for anim in animations:
            sx, sy = anim["start"]
            ex, ey = anim["end"]
            anim["tile"].x = sx + (ex - sx) * eased
            anim["tile"].y = sy + (ey - sy) * eased

        draw(window, tiles)

    # Finalize positions and construct new tile map, handling merges
    result_tiles = {}
    handled_merge_targets = set()
    for anim in animations:
        tile = anim["tile"]
        dest_key = anim["dest_key"]
        # Snap to exact grid position
        dest_row = int(dest_key[0])
        dest_col = int(dest_key[1])
        tile.row = dest_row
        tile.col = dest_col
        tile.set_xy_from_grid()

    # Build mapping of destination keys to lists of tiles that landed there (to resolve merges)
    landing = {}
    for anim in animations:
        k = anim["dest_key"]
        landing.setdefault(k, []).append(anim)

    for k, items in landing.items():
        if len(items) == 1 and not items[0]["is_merged"]:
            t = items[0]["tile"]
            result_tiles[k] = t
        else:
            # merged cell: compute new value and keep one tile object
            # pick the first tile object as the survivor
            survivor = items[0]["tile"]
            total = 0
            for it in items:
                total += it["tile"].value
            # In 2048, merging two equal tiles yields double a single value
            # so total should be 2 * single value; but computing as sum is safe
            survivor.value = total
            result_tiles[k] = survivor

    # Replace tiles dict contents
    tiles.clear()
    for k, t in result_tiles.items():
        tiles[k] = t

    # animation finished — allow input again
    ANIMATING = False

    return end_move(tiles)


def end_move(tiles):
    if len(tiles) == 16:
        return "lost"

    row, col = get_random_pos(tiles)
    tiles[f"{row}{col}"] = Tile(random.choice([2,4]), row, col)


def update_tiles(window,tiles, sorted_tiles):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.col}"] = tile

    draw(window, tiles)

def generate_tiles():
    tiles = {}
    for _ in range(2):
        row,col = get_random_pos(tiles)
        tiles[f"{row}{col}"] = Tile(2, row, col)

    return tiles




def main(window):
    clock = pygame.time.Clock()
    run = True

    tiles = generate_tiles()

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                # ignore input while animations are running
                if not ANIMATING:
                    if event.key == pygame.K_LEFT:
                        move_tiles(window, tiles, clock, "left")
                    elif event.key == pygame.K_RIGHT:
                        move_tiles(window, tiles, clock, "right")
                    elif event.key == pygame.K_UP:
                        move_tiles(window, tiles, clock, "up")
                    elif event.key == pygame.K_DOWN:
                        move_tiles(window, tiles, clock, "down")

        draw(window, tiles)

    pygame.quit()


if __name__ == "__main__":
    main(WINDOW)