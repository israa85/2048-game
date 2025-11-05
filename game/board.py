from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Iterable
from .tile import Tile
from .constants import ROWS, COLS
import random

Key = str
Pos = Tuple[int, int]


@dataclass
class Animation:
    tile: Tile
    start: Tuple[float, float]
    end: Tuple[float, float]
    is_merging: bool = False


class Board:
    def __init__(self):
        self.tiles: Dict[Key, Tile] = {}
        self._spawn_initial()

    def _key(self, r: int, c: int) -> Key:
        return f"{r}{c}"

    def _spawn_initial(self):
        self.spawn_random()
        self.spawn_random()

    def spawn_random(self, value: int = None):
        empty = [
            (r, c)
            for r in range(ROWS)
            for c in range(COLS)
            if self._key(r, c) not in self.tiles
        ]
        if not empty:
            return
        r, c = random.choice(empty)
        val = value or random.choice([2, 4])
        tile = Tile(val, r, c)
        self.tiles[self._key(r, c)] = tile

    def move(self, direction: str) -> Optional[List[Animation]]:
        """Return list of animations if move changed board, else None."""
        # Convert current board to 2D array of values
        old_grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        for r in range(ROWS):
            for c in range(COLS):
                key = self._key(r, c)
                if key in self.tiles:
                    old_grid[r][c] = self.tiles[key].value

        # Apply move logic to get new grid
        new_grid, animations = self._apply_move(old_grid, direction)

        # Check if board actually changed
        if old_grid == new_grid:
            return None

        # Rebuild tiles dictionary from new grid
        new_tiles: Dict[Key, Tile] = {}
        for r in range(ROWS):
            for c in range(COLS):
                if new_grid[r][c] != 0:
                    tile = Tile(new_grid[r][c], r, c)
                    new_tiles[self._key(r, c)] = tile

        self.tiles = new_tiles

        # Snap all tiles to grid
        for tile in self.tiles.values():
            tile.update_pos()

        return animations

    def _apply_move(
        self, grid: List[List[int]], direction: str
    ) -> Tuple[List[List[int]], List[Animation]]:
        """Apply move to grid and generate animations."""
        from .constants import RECT_WIDTH, RECT_HEIGHT

        animations = []
        new_grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

        if direction == "left":
            for r in range(ROWS):
                line = [grid[r][c] for c in range(COLS)]
                new_line = self._collapse_line(line)
                for c, val in enumerate(new_line):
                    new_grid[r][c] = val

                # Generate animations for this row
                self._generate_row_animations(grid, new_grid, r, direction, animations)

        elif direction == "right":
            for r in range(ROWS):
                line = [grid[r][c] for c in range(COLS - 1, -1, -1)]
                new_line = self._collapse_line(line)
                for i, val in enumerate(new_line):
                    c = COLS - 1 - i
                    new_grid[r][c] = val

                self._generate_row_animations(grid, new_grid, r, direction, animations)

        elif direction == "up":
            for c in range(COLS):
                line = [grid[r][c] for r in range(ROWS)]
                new_line = self._collapse_line(line)
                for r, val in enumerate(new_line):
                    new_grid[r][c] = val

                self._generate_col_animations(grid, new_grid, c, direction, animations)

        elif direction == "down":
            for c in range(COLS):
                line = [grid[r][c] for r in range(ROWS - 1, -1, -1)]
                new_line = self._collapse_line(line)
                for i, val in enumerate(new_line):
                    r = ROWS - 1 - i
                    new_grid[r][c] = val

                self._generate_col_animations(grid, new_grid, c, direction, animations)

        return new_grid, animations

    def _collapse_line(self, line: List[int]) -> List[int]:
        """Collapse a line (merge and slide), returns new line with same length."""
        # Filter out zeros
        filtered = [x for x in line if x != 0]

        # Merge adjacent equal values
        merged = []
        i = 0
        while i < len(filtered):
            if i + 1 < len(filtered) and filtered[i] == filtered[i + 1]:
                merged.append(filtered[i] * 2)
                i += 2
            else:
                merged.append(filtered[i])
                i += 1

        # Pad with zeros to original length
        return merged + [0] * (len(line) - len(merged))

    def _generate_row_animations(
        self,
        old_grid: List[List[int]],
        new_grid: List[List[int]],
        row: int,
        direction: str,
        animations: List[Animation],
    ):
        """Generate animations for a row move."""
        from .constants import RECT_WIDTH, RECT_HEIGHT

        old_tiles = {}
        for c in range(COLS):
            if old_grid[row][c] != 0:
                key = self._key(row, c)
                if key in self.tiles:
                    old_tiles[c] = self.tiles[key]

        # Track which old positions contributed to each new position
        old_positions = [c for c in range(COLS) if old_grid[row][c] != 0]
        new_positions = [c for c in range(COLS) if new_grid[row][c] != 0]

        if direction == "left":
            old_positions.sort()
        else:  # right
            old_positions.sort(reverse=True)

        # Map old tiles to new positions
        old_idx = 0
        for new_c in new_positions:
            new_val = new_grid[row][new_c]
            dest_pos = (new_c * RECT_WIDTH, row * RECT_HEIGHT)

            # Check if this is a merge (two tiles with half the value)
            if old_idx + 1 < len(old_positions):
                c1, c2 = old_positions[old_idx], old_positions[old_idx + 1]
                if c1 in old_tiles and c2 in old_tiles:
                    if (
                        old_tiles[c1].value == old_tiles[c2].value
                        and old_tiles[c1].value * 2 == new_val
                    ):
                        # Merge: both tiles animate to same spot
                        animations.append(
                            Animation(
                                tile=old_tiles[c1],
                                start=(old_tiles[c1].x, old_tiles[c1].y),
                                end=dest_pos,
                                is_merging=True,
                            )
                        )
                        animations.append(
                            Animation(
                                tile=old_tiles[c2],
                                start=(old_tiles[c2].x, old_tiles[c2].y),
                                end=dest_pos,
                                is_merging=True,
                            )
                        )
                        old_idx += 2
                        continue

            # No merge: single tile moves
            if old_idx < len(old_positions):
                old_c = old_positions[old_idx]
                if old_c in old_tiles:
                    animations.append(
                        Animation(
                            tile=old_tiles[old_c],
                            start=(old_tiles[old_c].x, old_tiles[old_c].y),
                            end=dest_pos,
                            is_merging=False,
                        )
                    )
                old_idx += 1

    def _generate_col_animations(
        self,
        old_grid: List[List[int]],
        new_grid: List[List[int]],
        col: int,
        direction: str,
        animations: List[Animation],
    ):
        """Generate animations for a column move."""
        from .constants import RECT_WIDTH, RECT_HEIGHT

        old_tiles = {}
        for r in range(ROWS):
            if old_grid[r][col] != 0:
                key = self._key(r, col)
                if key in self.tiles:
                    old_tiles[r] = self.tiles[key]

        old_positions = [r for r in range(ROWS) if old_grid[r][col] != 0]
        new_positions = [r for r in range(ROWS) if new_grid[r][col] != 0]

        if direction == "up":
            old_positions.sort()
        else:  # down
            old_positions.sort(reverse=True)

        old_idx = 0
        for new_r in new_positions:
            new_val = new_grid[new_r][col]
            dest_pos = (col * RECT_WIDTH, new_r * RECT_HEIGHT)

            # Check if this is a merge
            if old_idx + 1 < len(old_positions):
                r1, r2 = old_positions[old_idx], old_positions[old_idx + 1]
                if r1 in old_tiles and r2 in old_tiles:
                    if (
                        old_tiles[r1].value == old_tiles[r2].value
                        and old_tiles[r1].value * 2 == new_val
                    ):
                        animations.append(
                            Animation(
                                tile=old_tiles[r1],
                                start=(old_tiles[r1].x, old_tiles[r1].y),
                                end=dest_pos,
                                is_merging=True,
                            )
                        )
                        animations.append(
                            Animation(
                                tile=old_tiles[r2],
                                start=(old_tiles[r2].x, old_tiles[r2].y),
                                end=dest_pos,
                                is_merging=True,
                            )
                        )
                        old_idx += 2
                        continue

            # No merge: single tile moves
            if old_idx < len(old_positions):
                old_r = old_positions[old_idx]
                if old_r in old_tiles:
                    animations.append(
                        Animation(
                            tile=old_tiles[old_r],
                            start=(old_tiles[old_r].x, old_tiles[old_r].y),
                            end=dest_pos,
                            is_merging=False,
                        )
                    )
                old_idx += 1

    def is_game_over(self) -> bool:
        if len(self.tiles) < ROWS * COLS:
            return False
        for r in range(ROWS):
            for c in range(COLS):
                val = self.tiles[self._key(r, c)].value
                for dr, dc in [(0, 1), (1, 0)]:
                    nr, nc = r + dr, c + dc
                    if (
                        nr < ROWS
                        and nc < COLS
                        and self.tiles[self._key(nr, nc)].value == val
                    ):
                        return False
        return True

    def get_tiles(self) -> Iterable[Tile]:
        return self.tiles.values()
