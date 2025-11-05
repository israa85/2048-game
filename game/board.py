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
    merge_target: Optional[Tile] = None


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
        animations = []

        if direction == "left":
            for r in range(ROWS):
                line = [self.tiles.get(self._key(r, c)) for c in range(COLS)]
                new_line, anims = self._slide_line(line, direction)
                animations.extend(anims)
                self._apply_line(r, 0, new_line, direction)
        elif direction == "right":
            for r in range(ROWS):
                line = [
                    self.tiles.get(self._key(r, c)) for c in range(COLS - 1, -1, -1)
                ]
                new_line, anims = self._slide_line(line, direction)
                animations.extend(anims)
                self._apply_line(r, COLS - 1, new_line, direction, reverse=True)
        elif direction == "up":
            for c in range(COLS):
                line = [self.tiles.get(self._key(r, c)) for r in range(ROWS)]
                new_line, anims = self._slide_line(line, direction)
                animations.extend(anims)
                self._apply_line(0, c, new_line, direction, vertical=True)
        elif direction == "down":
            for c in range(COLS):
                line = [
                    self.tiles.get(self._key(r, c)) for r in range(ROWS - 1, -1, -1)
                ]
                new_line, anims = self._slide_line(line, direction)
                animations.extend(anims)
                self._apply_line(
                    ROWS - 1, c, new_line, direction, vertical=True, reverse=True
                )

        if not animations:
            return None

        # Finalize merge values
        merge_map: Dict[int, Tile] = {}
        for anim in animations:
            if anim.merge_target:
                merge_map[id(anim.merge_target)] = anim.merge_target

        for target in merge_map.values():
            target.value *= 2
            if target.merge_partner:
                key = self._key(target.merge_partner.row, target.merge_partner.col)
                self.tiles.pop(key, None)

        # Snap all tiles to grid
        for tile in self.tiles.values():
            tile.update_pos()
        return animations

    def _slide_line(
        self, line: List[Optional[Tile]], direction: str
    ) -> Tuple[List[Tile], List[Animation]]:
        from .constants import RECT_WIDTH, RECT_HEIGHT

        filtered = [t for t in line if t is not None]
        new_line: List[Tile] = []
        animations: List[Animation] = []
        i = 0

        while i < len(filtered):
            current = filtered[i]
            if i + 1 < len(filtered) and filtered[i + 1].value == current.value:

                merged = Tile(current.value, current.row, current.col)
                merged.merge_partner = filtered[i + 1]
                new_line.append(merged)

                # Both tiles animate to same spot
                dest_idx = len(new_line) - 1
                dest_pos = self._dest_pos(dest_idx, direction, current.row, current.col)

                animations.append(
                    Animation(
                        tile=current,
                        start=(current.x, current.y),
                        end=dest_pos,
                        merge_target=merged,
                    )
                )
                animations.append(
                    Animation(
                        tile=filtered[i + 1],
                        start=(filtered[i + 1].x, filtered[i + 1].y),
                        end=dest_pos,
                        merge_target=merged,
                    )
                )
                i += 2
            else:
                new_line.append(current)
                dest_idx = len(new_line) - 1
                dest_pos = self._dest_pos(dest_idx, direction, current.row, current.col)
                animations.append(
                    Animation(tile=current, start=(current.x, current.y), end=dest_pos)
                )
                i += 1

        return new_line, animations

    def _dest_pos(
        self, idx: int, direction: str, row: int, col: int
    ) -> Tuple[float, float]:
        from .constants import RECT_WIDTH, RECT_HEIGHT

        if direction in ("left", "right"):
            c = idx if direction == "left" else COLS - 1 - idx
            return (c * RECT_WIDTH, row * RECT_HEIGHT)
        else:  # up/down
            r = idx if direction == "up" else ROWS - 1 - idx
            return (col * RECT_WIDTH, r * RECT_HEIGHT)

    def _apply_line(
        self,
        start_r: int,
        start_c: int,
        line: List[Tile],
        direction: str,
        vertical: bool = False,
        reverse: bool = False,
    ):
        self.tiles = {k: t for k, t in self.tiles.items() if t not in line}
        for i, tile in enumerate(line):
            if vertical:
                r = i if not reverse else ROWS - 1 - i
                c = start_c
            else:
                r = start_r
                c = i if not reverse else COLS - 1 - i
            tile.row, tile.col = r, c
            self.tiles[self._key(r, c)] = tile

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
