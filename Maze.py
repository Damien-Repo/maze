
import pygame
import random

from Cell import Cell

class Maze():

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

    def _find_neighbor(self):
        neighbors = []

        up_cell = self._get_neighbor(self._current_cell.x, self._current_cell.y - 1)
        down_cell = self._get_neighbor(self._current_cell.x, self._current_cell.y + 1)
        right_cell = self._get_neighbor(self._current_cell.x + 1, self._current_cell.y)
        left_cell = self._get_neighbor(self._current_cell.x - 1, self._current_cell.y)

        if up_cell and not up_cell.is_visited:
            neighbors.append(up_cell)
        if down_cell and not down_cell.is_visited:
            neighbors.append(down_cell)
        if right_cell and not right_cell.is_visited:
            neighbors.append(right_cell)
        if left_cell and not left_cell.is_visited:
            neighbors.append(left_cell)

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

    def update(self):

        self._current_cell.visit()

        next_cell = self._find_neighbor()
        if next_cell != None:
            self._remove_wall(self._current_cell, next_cell)
            self._stack_pull(self._current_cell)
            self._current_cell = next_cell
        elif len(self._stack) > 0:
            self._current_cell = self._stack_pop()

    def draw(self, screen):
        for cell in self._cells:
            cell.draw(screen)

        self._current_cell.hightlight(screen)

        pygame.draw.rect(screen, Cell.WALL_COLOR, screen.get_rect(), 1)
