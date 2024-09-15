
import random

import pygame

from .Cell import Cell


class Map():

    # neighbor offsets with cardinality of the wall to the cell
    _NEIGHBOR_OFFSETS = {
        (0, -1): 'S',
        (0, +1): 'N',
        (+1, 0): 'W',
        (-1, 0): 'E',
    }

    def __init__(self, screen, cols, rows):

        w, h = screen.get_size()
        Cell.SIZE = min(w // cols, h // rows)
        assert(Cell.SIZE >= Cell.SIZE_LIMIT_MIN), f'cols/rows cannot be less than: cols={w // Cell.SIZE_LIMIT_MIN}, rows={h // Cell.SIZE_LIMIT_MIN}'

        self.cols = cols
        self.rows = rows

        self._cells = []
        for y in range(0, self.rows):
            for x in range(0, self.cols):
                cell = Cell(x, y)
                self._cells.append(cell)

    def __len__(self):
        return self.cols * self.rows

    def get_cell(self, x, y):
        if x < 0 or y < 0 or \
           x > self.cols - 1 or y > self.rows - 1:
            return None

        return self._cells[y * self.cols + x]

    def get_random_cell(self):
        return random.sample(self._cells, 1)[0]

    def get_random_cell_pos(self):
        return (random.randint(0, self.cols - 1), random.randint(0, self.rows - 1))

    def _is_neighbor(self, cell, wall_cardinality=None):
        if cell is None:
            return False

        if wall_cardinality is not None:
            return not cell.is_wall(wall_cardinality)

        return not cell.is_visited

    def discover_new_neighbors(self, cell):
        neighbors = []

        for offset in self._NEIGHBOR_OFFSETS:
            n = self.get_cell(cell.x + offset[0], cell.y + offset[1])
            if n is not None and not n.is_visited:
                neighbors.append(n)

        return neighbors

    def find_neighbors(self, cell):
        neighbors = []

        for offset, cardinality in self._NEIGHBOR_OFFSETS.items():
            n = self.get_cell(cell.x + offset[0], cell.y + offset[1])
            if n is not None and not n.is_wall(cardinality):
                neighbors.append(n)

        return neighbors

    def draw(self, screen):
        pygame.draw.rect(screen, Cell.WALL_COLOR, screen.get_rect(), 1)
