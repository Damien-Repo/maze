
import pygame
from pygame.math import Vector2 as Vec

from .Cell import Cell

class AStarCell():

    def __init__(self, cell, previous=None):
        self._cell = cell

        self.previous_cell = previous
        self._last_next_cell = None
        self._last_link_cells_update = None

        self.length = previous.length + 1 if previous is not None else 0

        self.f = float('inf')
        self.g = float('inf')
        self.h = 0

    def __eq__(self, other):
        return self._cell.x == other._cell.x and self._cell.y == other._cell.y

    def __hash__(self):
        return hash((self._cell.x, self._cell.y))

    def __str__(self):
        return f'{self.__class__.__name__}: {self._cell}'

    @property
    def x(self):
        return self._cell.x

    @property
    def y(self):
        return self._cell.y

    def get_next_cell(self):
        return self._last_next_cell

    def get_next_stable_cell(self, current_update_count, stable_min_duration=100):
        if self._last_next_cell is None:
            return

        if current_update_count - self._last_link_cells_update > stable_min_duration:
            return self.get_next_cell()

    def link_next_cell(self, cell, update_count):
        if self._last_next_cell is None or cell != self._last_next_cell:
            self._last_next_cell = cell
            self._last_link_cells_update = update_count

    def heuristic(self, other):
        return Vec(self.x, self.y).distance_to(Vec(other.x, other.y))

    def get_path(self):
        current = self
        while current is not None:
            yield current
            current = current.previous_cell

    def draw(self, screen, prev_cell=None, next_cell=None, stable=False):
        if prev_cell is None and next_cell is None:
            return

        if prev_cell is None:
            prev_cell = self
            cur_cell = next_cell
        else:
            # prev_cell = prev_cell
            cur_cell = self

        prev_x, prev_y = (prev_cell.x * Cell.SIZE, prev_cell.y * Cell.SIZE)
        cur_x, cur_y = (cur_cell.x * Cell.SIZE, cur_cell.y * Cell.SIZE)

        half_cell_size = Cell.SIZE // 2
        pos_prev = (prev_x + half_cell_size, prev_y + half_cell_size)
        pos_cur = (cur_x + half_cell_size, cur_y + half_cell_size)

        color = Pathfinder.COLOR_STABLE_PATH if stable else Pathfinder.COLOR_PATH

        # draw path line
        thickness = max(Cell.SIZE // 4, 1)
        pygame.draw.line(screen, color, pos_prev, pos_cur, thickness)

        # draw round corners
        thickness = max(Cell.SIZE // 8, 1)
        pygame.draw.circle(screen, color, pos_prev, thickness - 1)


class Pathfinder():

    COLOR_START       = pygame.Color('green')
    COLOR_END         = pygame.Color('red')
    COLOR_PATH        = pygame.Color('blue')
    COLOR_STABLE_PATH = pygame.Color('cyan')

    def __init__(self, map_grid, start_pos=None, end_pos=None):

        if start_pos is None:
            start_pos = map_grid.get_random_cell_pos()
        if end_pos is None:
            end_pos = map_grid.get_random_cell_pos()
            while Vec(start_pos).distance_to(Vec(end_pos)) <= min(map_grid.cols, map_grid.rows) // 4:
                end_pos = map_grid.get_random_cell_pos()

        self._update_count = 0

        self._cell_start = AStarCell(map_grid.get_cell(*start_pos))
        self._cell_end = AStarCell(map_grid.get_cell(*end_pos))
        self._cell_cur = None

        self._cell_start.g = 0
        self._cell_start.f = self._cell_start.heuristic(self._cell_start)

        self._stable_path = []
        self._last_stable = None

        self._stable_min_duration = max(min(map_grid.cols, map_grid.rows) // 2, 1)
        self._last_stable = self._cell_start
        self._last_rendered_stable = self._cell_start

        self._map = map_grid

        self._surface_path = pygame.Surface((self._map.cols * Cell.SIZE, self._map.rows * Cell.SIZE), flags=pygame.SRCALPHA)
        self._surface_stable_path = self._surface_path.copy()
        self._surface_stable_path.fill((0, 0, 0, 0))
        self._surface_points = None
        self._surface_debug_set = self._surface_path.copy()
        self._surface_debug_set.fill((0, 0, 0, 0))

        self._open_set = set([self._cell_start])
        self._closed_set = set()
        self._debug_set = set()

        self._winner = None

        self.is_final_path_full_rendered = False

    def __len__(self):
        if self._cell_cur is None:
            return 0
        return self._cell_cur.length

    def path_found(self):
        return self._winner is not None and self._last_rendered_stable == self._winner

    def _A_star(self):
        if len(self._open_set) == 0:
            return

        self._cell_cur = min(self._open_set, key=lambda cell: cell.f)

        if self._cell_cur == self._cell_end:
            # Finish
            self._winner = self._cell_cur
            return

        self._open_set.remove(self._cell_cur)
        self._closed_set.add(self._cell_cur)
        self._debug_set.add(self._cell_cur)

        for neighbor in self._map.find_neighbors(self._cell_cur):
            n = AStarCell(neighbor, previous=self._cell_cur)

            if n in self._closed_set:
                continue

            g_score = self._cell_cur.g + self._cell_cur.heuristic(n)

            if g_score >= n.g:
                continue

            n.g = g_score
            n.h = n.heuristic(self._cell_end)
            n.f = n.g + n.h

            self._open_set.add(n)
            self._debug_set.add(n)

    def _update_stable_path(self):
        prev = None
        for p in self._cell_cur.get_path():
            if prev is not None:
                p.link_next_cell(prev, self._update_count)
            if p == self._last_stable:
                break
            prev = p

        cur = self._last_stable

        while cur != self._cell_cur:
            next_cell = cur.get_next_stable_cell(self._update_count, self._stable_min_duration)

            if next_cell is None:
                break
            cur = next_cell

            self._last_stable = cur

    def _render_stable_path(self, step_max=10):
        cur = self._last_rendered_stable
        step_count = 0

        while cur != self._last_stable:

            if step_count > step_max:
                break

            next_cell = cur.get_next_stable_cell(self._update_count, self._stable_min_duration)
            cur.draw(self._surface_stable_path, next_cell=next_cell, stable=True)
            cur = next_cell
            self._last_rendered_stable = cur
            step_count += 1

    def update(self, multiple_update_counter=1):
        assert(multiple_update_counter > 0)

        for _ in range(0, multiple_update_counter):
            if self.path_found():
                return

            self._update_count += 1

            self._A_star()
            self._update_stable_path()
            self._render_stable_path()

    def _render_path_gen(self, cur_cell_to_render, last_cell_to_render, depth_max):
        prev = None
        for depth, p in enumerate(cur_cell_to_render.get_path()):
            if depth_max is not None and depth > depth_max:
                break

            p.draw(self._surface_path, prev)
            yield p

            if p == last_cell_to_render:
                break

            prev = p

    def _render_path(self, last_cell_to_render=None, depth_max=100):
        self._surface_path.fill((0, 0, 0, 0))
        for _ in self._render_path_gen(self._cell_cur, last_cell_to_render, depth_max):
            pass

    def draw_full_path(self, screen):
        assert(self._cell_cur is not None)
        if self.is_final_path_full_rendered:
            return

        for cell in self._render_path_gen(self._cell_cur, self._cell_start, max(self._cell_cur.length // 60, 50)):
            self._cell_cur = cell

        if self._cell_cur == self._cell_start:
            self.is_final_path_full_rendered = True

        screen.blit(self._surface_path, (0, 0))

    def _draw_start_end_points(self):
        if self._surface_points is not None:
            return

        self._surface_points = self._surface_path.copy()
        self._surface_points.fill((0, 0, 0, 0))

        half_cell_size = Cell.SIZE // 2 + 1
        radius = max(Cell.SIZE // 4, 1)

        assert(radius >= 1), f'Radius: {radius}'
        assert(Cell.SIZE // 2 >= 1), f'Size: {Cell.SIZE // 2}'

        # Start point
        start_x, start_y = (self._cell_start.x * Cell.SIZE, self._cell_start.y * Cell.SIZE)
        start_pos = (start_x + half_cell_size, start_y + half_cell_size)
        pygame.draw.circle(self._surface_points, Pathfinder.COLOR_START, start_pos, radius)

        # End point
        end_x, end_y = (self._cell_end.x * Cell.SIZE, self._cell_end.y * Cell.SIZE)
        end_pos = (end_x + half_cell_size, end_y + half_cell_size)
        pygame.draw.circle(self._surface_points, Pathfinder.COLOR_END, end_pos, radius)

    def _draw_stable_path(self):
        pass

    def _draw_path(self):
        if self._cell_cur is None:
            return

        self._render_path(last_cell_to_render=self._last_stable, depth_max=10)

    def _draw_debug_set(self):
        for cell in self._debug_set:
            color = pygame.Color('cyan')
            if cell in self._closed_set:
                color = pygame.Color('black')
            elif cell in self._open_set:
                color = pygame.Color('green')
            elif cell == self._cell_cur:
                color = pygame.Color('red')
            self._surface_debug_set.fill(color, pygame.Rect(cell.x * Cell.SIZE, cell.y * Cell.SIZE, Cell.SIZE, Cell.SIZE))

        self._debug_set.clear()

    def draw(self, screen, debug=False):
        self._draw_stable_path()
        self._draw_path()
        self._draw_start_end_points()

        if debug:
            self._draw_debug_set()
            screen.blit(self._surface_debug_set, (0, 0))

        screen.blit(self._surface_stable_path, (0, 0))
        screen.blit(self._surface_path, (0, 0))
        screen.blit(self._surface_points, (0, 0))




