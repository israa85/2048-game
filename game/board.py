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
        self._pending_new_grid: Optional[List[List[int]]] = None
        self._pending_map: Optional[Dict[Key, Tile]] = None
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

    def move(self, direction: str) -> bool:
        """Apply move, set per-tile animations, and defer grid update until finalize_move.
        Returns True if the board changed."""
        # Build old grid
        old_grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        for r in range(ROWS):
            for c in range(COLS):
                key = self._key(r, c)
                if key in self.tiles:
                    old_grid[r][c] = self.tiles[key].value

        # Helper to process a line of indices in traversal order
        def process_line(indices: List[Tuple[int, int]]):
            # Collect existing tiles in order
            line_tiles: List[Tile] = []
            for (r, c) in indices:
                t = self.tiles.get(self._key(r, c))
                if t and t.value != 0:
                    line_tiles.append(t)

            result_values: List[int] = []
            result_tiles: List[Tile] = []
            i = 0
            target_idx = 0
            while i < len(line_tiles):
                cur = line_tiles[i]
                if i + 1 < len(line_tiles) and line_tiles[i + 1].value == cur.value:
                    # Merge cur and next
                    nxt = line_tiles[i + 1]
                    dest_r, dest_c = indices[target_idx]
                    # Animate both to the same destination
                    cur.set_animation(cur.row, cur.col, dest_r, dest_c)
                    nxt.set_animation(nxt.row, nxt.col, dest_r, dest_c)
                    # Survivor is cur, doubled value
                    result_values.append(cur.value * 2)
                    result_tiles.append(cur)
                    i += 2
                    target_idx += 1
                else:
                    # Move single tile
                    dest_r, dest_c = indices[target_idx]
                    cur.set_animation(cur.row, cur.col, dest_r, dest_c)
                    result_values.append(cur.value)
                    result_tiles.append(cur)
                    i += 1
                    target_idx += 1

            # Pad with zeros to full length
            while len(result_values) < len(indices):
                result_values.append(0)

            return result_values, result_tiles

        new_grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        dest_map: Dict[Key, Tile] = {}

        changed = False
        if direction == "left":
            for r in range(ROWS):
                indices = [(r, c) for c in range(COLS)]
                values, tiles_seq = process_line(indices)
                for c, val in enumerate(values):
                    new_grid[r][c] = val
                # Record survivors and their destination mapping
                write_idx = 0
                for t in tiles_seq:
                    dr, dc = indices[write_idx]
                    dest_map[self._key(dr, dc)] = t
                    write_idx += 1
                if [old_grid[r][c] for c in range(COLS)] != values:
                    changed = True

        elif direction == "right":
            for r in range(ROWS):
                indices = [(r, c) for c in range(COLS - 1, -1, -1)]
                values, tiles_seq = process_line(indices)
                # Place values back in right-justified positions
                for i, val in enumerate(values):
                    c = COLS - 1 - i
                    new_grid[r][c] = val
                # Map survivors to their destination in right order
                write_idx = 0
                for t in tiles_seq:
                    dr, dc = indices[write_idx]
                    dest_map[self._key(dr, dc)] = t
                    write_idx += 1
                if [old_grid[r][c] for c in range(COLS)] != [new_grid[r][c] for c in range(COLS)]:
                    changed = True

        elif direction == "up":
            for c in range(COLS):
                indices = [(r, c) for r in range(ROWS)]
                values, tiles_seq = process_line(indices)
                for r, val in enumerate(values):
                    new_grid[r][c] = val
                write_idx = 0
                for t in tiles_seq:
                    dr, dc = indices[write_idx]
                    dest_map[self._key(dr, dc)] = t
                    write_idx += 1
                if [old_grid[r][c] for r in range(ROWS)] != [new_grid[r][c] for r in range(ROWS)]:
                    changed = True

        elif direction == "down":
            for c in range(COLS):
                indices = [(r, c) for r in range(ROWS - 1, -1, -1)]
                values, tiles_seq = process_line(indices)
                for i, val in enumerate(values):
                    r = ROWS - 1 - i
                    new_grid[r][c] = val
                write_idx = 0
                for t in tiles_seq:
                    dr, dc = indices[write_idx]
                    dest_map[self._key(dr, dc)] = t
                    write_idx += 1
                if [old_grid[r][c] for r in range(ROWS)] != [new_grid[r][c] for r in range(ROWS)]:
                    changed = True

        if not changed:
            return False

        # Defer applying new grid until after animation
        self._pending_new_grid = new_grid
        self._pending_map = dest_map
        return True

    def finalize_move(self):
        """Apply the pending grid after animations complete: update tile values and positions."""
        if self._pending_new_grid is None or self._pending_map is None:
            return
        new_grid = self._pending_new_grid
        dest_map = self._pending_map
        new_tiles: Dict[Key, Tile] = {}
        for r in range(ROWS):
            for c in range(COLS):
                val = new_grid[r][c]
                if val == 0:
                    continue
                key = self._key(r, c)
                t = dest_map.get(key)
                if t is None:
                    # Fallback create if missing (shouldn't happen)
                    t = Tile(val, r, c)
                else:
                    t.value = val
                    t.row = r
                    t.col = c
                    t.update_pos()
                new_tiles[key] = t
        self.tiles = new_tiles
        self._pending_new_grid = None
        self._pending_map = None

    def _apply_move_simple(self, grid: List[List[int]], direction: str) -> List[List[int]]:
        """Apply move to grid and return new grid."""
        new_grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

        if direction == "left":
            for r in range(ROWS):
                line = [grid[r][c] for c in range(COLS)]
                new_line = self._collapse_line(line)
                for c, val in enumerate(new_line):
                    new_grid[r][c] = val
        
        elif direction == "right":
            for r in range(ROWS):
                line = [grid[r][c] for c in range(COLS - 1, -1, -1)]
                new_line = self._collapse_line(line)
                for i, val in enumerate(new_line):
                    c = COLS - 1 - i
                    new_grid[r][c] = val
        
        elif direction == "up":
            for c in range(COLS):
                line = [grid[r][c] for r in range(ROWS)]
                new_line = self._collapse_line(line)
                for r, val in enumerate(new_line):
                    new_grid[r][c] = val
        
        elif direction == "down":
            for c in range(COLS):
                line = [grid[r][c] for r in range(ROWS - 1, -1, -1)]
                new_line = self._collapse_line(line)
                for i, val in enumerate(new_line):
                    r = ROWS - 1 - i
                    new_grid[r][c] = val
        
        return new_grid
    
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
