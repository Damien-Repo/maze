
from threading import Thread

import pygame
from pygame.math import Vector2 as Vec

from .Cell import Cell

class AStarCell():

    def __init__(self, cell, previous=None):
        self._cell = cell
        self.previous_cell = previous

        self.f = float('inf')
        self.g = float('inf')
        self.h = 0

    def __eq__(self, other):
        return self._cell.__eq__(getattr(other, '_cell', None))

    def __str__(self):
        return f'{self.__class__.__name__}: {self._cell}'

    @property
    def x(self):
        return self._cell.x

    @property
    def y(self):
        return self._cell.y

    def heuristic(self, other):
        return Vec(self.x, self.y).distance_to(Vec(other.x, other.y))

    def get_path(self):
        current = self
        while current is not None:
            yield current
            current = current.previous_cell

    def draw(self, screen, prev):
        if prev is None:
            return

        prev_x, prev_y = (prev.x * Cell.SIZE, prev.y * Cell.SIZE)
        cur_x, cur_y = (self.x * Cell.SIZE, self.y * Cell.SIZE)

        half_cell_size = Cell.SIZE // 2
        pos_prev = (prev_x + half_cell_size, prev_y + half_cell_size)
        pos_cur = (cur_x + half_cell_size, cur_y + half_cell_size)

        thickness = max(Cell.SIZE // 4, 1)
        pygame.draw.line(screen, Pathfinder.PATH_COLOR, pos_prev, pos_cur, thickness)
        thickness = max(Cell.SIZE // 8, 1)
        pygame.draw.circle(screen, Pathfinder.PATH_COLOR, pos_prev, thickness - 1)


class Pathfinder():

    START_COLOR = pygame.Color('green')
    END_COLOR   = pygame.Color('red')
    PATH_COLOR  = pygame.Color('blue')

    def __init__(self, map_grid, start_pos=None, end_pos=None):

        if start_pos is None:
            start_pos = map_grid.get_random_cell_pos()
        if end_pos is None:
            end_pos = map_grid.get_random_cell_pos()
            while Vec(start_pos).distance_to(Vec(end_pos)) <= min(map_grid.cols, map_grid.rows) // 4:
                end_pos = map_grid.get_random_cell_pos()

        self._start = AStarCell(map_grid.get_cell(*start_pos))
        self._end = AStarCell(map_grid.get_cell(*end_pos))
        self._cur = None

        self._start.g = 0
        self._start.f = self._start.heuristic(self._start)

        self._map = map_grid

        self._surface_path = pygame.Surface((self._map.cols * Cell.SIZE, self._map.rows * Cell.SIZE), flags=pygame.SRCALPHA)
        self._work_surface = self._surface_path.copy()

        self._open_set = [self._start]
        self._closed_set = []

        self._winner = None

        self._render_thread = None
        self._cell_drawing = None

    def path_found(self):
        return self._winner is not None

    def _A_star(self):
        if len(self._open_set) == 0:
            return

        self._cur = min(self._open_set, key=lambda o: o.f)

        if self._cur == self._end:
            # Finish
            self._winner = self._cur
            return

        self._open_set.remove(self._cur)
        self._closed_set.append(self._cur)

        for neighbor in self._map.find_neighbors(self._cur):
            n = AStarCell(neighbor, previous=self._cur)
            assert(n not in self._open_set)
            if n in self._closed_set:
                continue

            g_score = self._cur.g + self._cur.heuristic(n)

            if g_score >= n.g:
                continue

            n.g = g_score
            n.h = n.heuristic(self._end)
            n.f = n.g + n.h

            if n not in self._open_set:
                self._open_set.append(n)

    def update(self):
        if not self.path_found():
            self._A_star()

    def final_path_drawn(self):
        return self.path_found() and self._cell_drawing == self._winner and self._render_thread is None

    def _render_path(self):
        self._work_surface.fill((0, 0, 0, 0))
        prev = None
        for p in self._cell_drawing.get_path():
            p.draw(self._work_surface, prev)
            prev = p

    def draw(self, screen):

        # Path
        if self._cur is not None and self._render_thread is None:
            self._cell_drawing = self._cur
            self._render_thread = Thread(target=self._render_path)
            self._render_thread.start()

        if self._render_thread is not None and not self._render_thread.is_alive():
            self._render_thread.join()
            self._render_thread = None
            self._surface_path.fill((0, 0, 0, 0))
            self._surface_path.blit(self._work_surface, (0, 0))

        screen.blit(self._surface_path, (0, 0))

        # Start and End points
        start_x, start_y = (self._start.x * Cell.SIZE, self._start.y * Cell.SIZE)
        end_x, end_y = (self._end.x * Cell.SIZE, self._end.y * Cell.SIZE)

        half_cell_size = Cell.SIZE // 2 + 1
        start_pos = (start_x + half_cell_size, start_y + half_cell_size)
        end_pos = (end_x + half_cell_size, end_y + half_cell_size)

        radius = max(Cell.SIZE // 4, 1)

        assert(radius >= 1), f'Radius: {radius}'
        assert(Cell.SIZE // 2 >= 1), f'Size: {Cell.SIZE // 2}'

        pygame.draw.circle(screen, Pathfinder.START_COLOR, start_pos, radius)
        pygame.draw.circle(screen, Pathfinder.END_COLOR, end_pos, radius)
