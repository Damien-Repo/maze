
from os.path import exists as file_exists

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

    def __init__(self, screen_size, cols, rows, data_to_load=None):
        assert(data_to_load is None or (cols is None and rows is None))
        assert(data_to_load is not None or (cols is not None and rows is not None))
        assert(cols is None or cols > 0)
        assert(rows is None or rows > 0)

        self._cells = []
        self.cols = None
        self.rows = None

        if data_to_load is not None:
            self._load_existing_map(screen_size, data_to_load)
        else:
            self._generate_empty_map(screen_size, cols, rows)

    def __len__(self):
        return self.cols * self.rows

    def _init_dimensions(self, screen_size, cols, rows):
        screen_w, screen_h = screen_size

        if cols is None:
            cols = screen_w // 10
        if rows is None:
            rows = screen_h // 10

        Cell.SIZE = min(screen_w // cols, screen_h // rows)
        assert(Cell.SIZE >= Cell.SIZE_LIMIT_MIN), f'cols/rows cannot be less than: cols={screen_w // Cell.SIZE_LIMIT_MIN}, rows={screen_h // Cell.SIZE_LIMIT_MIN}'

        self.cols = cols
        self.rows = rows

    def _load_existing_map(self, screen_size, data_to_load):
        self._init_dimensions(screen_size, data_to_load['cols'], data_to_load['rows'])
        self._cells = [Cell.load(cell_data) for cell_data in data_to_load['cells']]

    def save(self):
        return {
            'cols': self.cols,
            'rows': self.rows,
            'cells': [cell.save() for cell in self._cells],
        }

    def _generate_empty_map(self, screen_size, cols, rows):
        self._init_dimensions(screen_size, cols, rows)

        for y in range(0, self.rows):
            for x in range(0, self.cols):
                cell = Cell(x, y)
                self._cells.append(cell)

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

    def draw_all_cells(self, screen):
        self.draw(screen)

        for cell in self._cells:
            cell.draw(screen)

    def draw(self, screen):
        pygame.draw.rect(screen, Cell.WALL_COLOR, screen.get_rect(), 1)
