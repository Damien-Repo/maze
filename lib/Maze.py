
import random

class MazeGenerator():
    #//TEMP voir pour pouvoir generer a partir de plusieurs points en parrallele
    pass


class Maze():

    def __init__(self, map_grid):
        self._map = map_grid

        self._current_cell = self._map.get_cell(0, 0)
        self._stack = [self._current_cell]

        self._visited_cells_count = 0

        self._cell_to_redraw = None

    @property
    def was_generated(self):
        return len(self._stack) == 0

    @property
    def progression(self):
        return self._visited_cells_count * 100.0 / len(self._map)

    def _stack_pull(self, cell):
        self._stack.append(cell)
        cell.stack()

    def _stack_pop(self):
        cell = self._stack.pop()
        cell.unstack()
        return cell

    def _find_random_neighbor(self, cell):
        neighbors = self._map.discover_new_neighbors(cell)
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
        self._visited_cells_count += 1

        self._cell_to_redraw = self._current_cell

        next_cell = self._find_random_neighbor(self._current_cell)
        if next_cell is not None:
            self._remove_wall(self._current_cell, next_cell)
            self._stack_pull(self._current_cell)
            self._visited_cells_count -= 1
            self._current_cell = next_cell
        elif len(self._stack) > 0:
            self._current_cell = self._stack_pop()

    def update(self):
        if self.was_generated:
            return

        self._update_generator()

    def draw(self, screen):
        if self._cell_to_redraw is not None:
            self._cell_to_redraw.draw(screen)
            self._cell_to_redraw = None

        if len(self._stack) > 0:
            self._current_cell.hightlight(screen)
