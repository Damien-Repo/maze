
import pygame
import random

from Cell import Cell
from Pathfinder import Pathfinder

class Maze():

    STATE_GENERATE = 1
    STATE_PATHFIND = 2

    def __init__(self, screen_size):
        w, h = screen_size

        self._grid_width = w // Cell.SIZE
        self._grid_height = h // Cell.SIZE

        self._cells = []
        for y in range(0, self._grid_height):
            for x in range(0, self._grid_width):
                cell = Cell(x, y)
                self._cells.append(cell)

        self._current_cell = self._cells[0]
        self._stack = []

        self._state = Maze.STATE_GENERATE

    def _init_pathfinder(self):
        self._state = Maze.STATE_PATHFIND
        self._pathfinder = Pathfinder(self._cells[0], self._cells[-1], self)

    def _stack_pull(self, cell):
        self._stack.append(cell)
        cell.stack()

    def _stack_pop(self):
        cell = self._stack.pop()
        cell.unstack()
        return cell

    def _get_neighbor(self, x, y):
        if x < 0 or y < 0 or\
           x > self._grid_width - 1 or y > self._grid_height - 1:
            return None

        return self._cells[x + y * self._grid_width]

    def _is_neighbor(self, cell, wall_cardinality):
        if cell == None:
            return False

        if self._state == Maze.STATE_GENERATE and not cell.is_visited:
            return True

        if self._state == Maze.STATE_PATHFIND and not cell.is_wall(wall_cardinality):
            return True

        return False

    def find_neighbors(self, cell):
        neighbors = []

        up_cell    = self._get_neighbor(cell.x    , cell.y - 1)
        down_cell  = self._get_neighbor(cell.x    , cell.y + 1)
        right_cell = self._get_neighbor(cell.x + 1, cell.y    )
        left_cell  = self._get_neighbor(cell.x - 1, cell.y    )

        if self._is_neighbor(up_cell, 'S'):    neighbors.append(up_cell)
        if self._is_neighbor(down_cell, 'N'):  neighbors.append(down_cell)
        if self._is_neighbor(right_cell, 'W'): neighbors.append(right_cell)
        if self._is_neighbor(left_cell, 'E'):  neighbors.append(left_cell)

        return neighbors

    def _find_random_neighbor(self, cell):
        neighbors = self.find_neighbors(cell)
        if len(neighbors) > 0:
            return random.sample(neighbors, 1)[0]

    def _remove_wall(self, cell_cur, cell_next):
        d_x = cell_cur.x - cell_next.x
        if d_x == 1:            # goto to left
            cell_cur.remove_wall('W')
            cell_next.remove_wall('E')
        elif d_x == -1:         # goto to right
            cell_cur.remove_wall('E')
            cell_next.remove_wall('W')

        d_y = cell_cur.y - cell_next.y
        if d_y == 1:            # goto to up
            cell_cur.remove_wall('N')
            cell_next.remove_wall('S')
        elif d_y == -1:         # goto to down
            cell_cur.remove_wall('S')
            cell_next.remove_wall('N')

    def _update_generator(self):
        self._current_cell.visit()

        next_cell = self._find_random_neighbor(self._current_cell)
        if next_cell != None:
            self._remove_wall(self._current_cell, next_cell)
            self._stack_pull(self._current_cell)
            self._current_cell = next_cell
        elif len(self._stack) > 0:
            self._current_cell = self._stack_pop()

    def update(self):
        if self._state == Maze.STATE_GENERATE:
            self._update_generator()
            if len(self._stack) == 0:
                self._init_pathfinder()
        elif self._state == Maze.STATE_PATHFIND:
            self._pathfinder.update()

    def draw(self, screen):
        for cell in self._cells:
            cell.draw(screen)

        if self._state == Maze.STATE_GENERATE:
            self._current_cell.hightlight(screen)
        elif self._state == Maze.STATE_PATHFIND:
            self._pathfinder.draw(screen)

        pygame.draw.rect(screen, Cell.WALL_COLOR, screen.get_rect(), 1)
