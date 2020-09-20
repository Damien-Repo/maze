
import pygame
from pygame.math import Vector2 as Vec

from Cell import Cell

class AStarCell():

    def __init__(self, cell, previous=None):
        self._cell = cell
        self._prev = previous

        self.f = float('inf')
        self.g = float('inf')
        self.h = 0
        self.vh = 0

    def __eq__(self, other):
        return self._cell.__eq__(getattr(other, '_cell', None))

    def __str__(self):
        return 'AStar%s {f=%s, g=%s, h=%s, vh=%s}' % (self._cell, self.f, self.g, self.h, self.vh)

    def __repr__(self):
        return self.__str__()

    @property
    def x(self):
        return self._cell.x

    @property
    def y(self):
        return self._cell.y

    def heuristic(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)

    def visual_distance(self, other):
        return Vec(self.x, self.y).distance_to(Vec(other.x, other.y))

    def draw(self, screen, prev):
        prev_x, prev_y = (prev.x * Cell.SIZE, prev.y * Cell.SIZE)
        cur_x, cur_y = (self.x * Cell.SIZE, self.y * Cell.SIZE)
        pos_prev = (prev_x + Cell.SIZE // 2, prev_y + Cell.SIZE // 2)
        pos_cur = (cur_x + Cell.SIZE // 2, cur_y + Cell.SIZE // 2)
        pygame.draw.line(screen, Pathfinder.PATH_COLOR, pos_prev, pos_cur, Cell.SIZE // 4)


class Pathfinder():

    START_COLOR = (  0, 255,   0)
    END_COLOR   = (255,   0,   0)
    PATH_COLOR  = (  0,   0, 255)

    def __init__(self, start, end, maze):
        self._start = AStarCell(start)
        self._end = AStarCell(end)

        self._start.g = 0
        self._start.heuristic(self._end)

        self._maze = maze

        self._open_set = [self._start]
        self._closed_set = []

        self._winner = None

    def _reconstruct_path(self, current):
        total_path = [current]
        while current in self._came_from.values():
            total_path.prepend(current)
        return total_path

    def _update_winner(self):
        if not getattr(self, '_cur', False): return

        best = None
        for o in self._open_set:
            '''
            if o.f < self._cur.f:
                print('BEST 1:', o.f, '<', self._cur.f)
                best = o
            '''
            if o.f == self._cur.f:
                if o.g > self._cur.g:
                    #print('BEST 2:', o.f, '|', o.g, '>', self._cur.g)
                    best = o

                elif o.g == self._cur.g and\
                     o.vh < self._cur.vh:
                    #print('BEST 3:', o.f, '|', o.g, '==', self._cur.g, 'and', o.vh, '<', self._cur.vh)
                    best = o

        #print('^^^^^^^-------------')
        return best

    def _A_star(self):
        if len(self._open_set) == 0:
            return

        current = self._update_winner()
        if current == None:
            current = self._open_set.pop()
        self._cur = current

        if current == self._end:
            # Finish
            self._winner = current
            return current

        #print('open_set:', self._open_set, '| current:', current)
        #print('closed_set:', self._closed_set)
        '''
        try:
            self._open_set.remove(current)
        except ValueError:
            pass
        '''
        self._closed_set.append(current)

        for neighbor in self._maze.find_neighbors(current):
            n = AStarCell(neighbor, previous=current)

            if n in self._closed_set:
                continue

            #print('g_score =', current.g, '+', current.heuristic(n))
            g_score = current.g + current.heuristic(n)

            if g_score >= n.g:
                #print('passe', g_score, n.g)
                continue

            #print('NOOOOO:', g_score, '<', n.g)
            n.g = g_score
            n.h = n.heuristic(self._end)
            n.vh = n.visual_distance(self._end)
            n.f = n.g + n.h

            if n not in self._open_set:
                self._open_set.append(n)

        #print('END open_set:', self._open_set, '| n:', n)
        #print('END closed_set:', self._closed_set)

    def update(self):
        if self._winner == None:
            self._A_star()

    def _reconstruct_path(self):
        if not getattr(self, '_cur', False):
            return []

        def _gen():
            current = self._cur
            while current:
                yield current
                current = current._prev

        return _gen()

    def draw(self, screen):

        # Path
        prev = None
        for p in self._reconstruct_path():
            if prev == None:
                prev = p
                continue
            p.draw(screen, prev)
            prev = p

        # Start and End points
        start_x, start_y = (self._start.x * Cell.SIZE, self._start.y * Cell.SIZE)
        end_x, end_y = (self._end.x * Cell.SIZE, self._end.y * Cell.SIZE)
        start_pos = (start_x + Cell.SIZE // 2, start_y + Cell.SIZE // 2)
        end_pos = (end_x + Cell.SIZE // 2, end_y + Cell.SIZE // 2)
        radius = Cell.SIZE // 4
        pygame.draw.circle(screen, Pathfinder.START_COLOR, start_pos, radius)
        pygame.draw.circle(screen, Pathfinder.END_COLOR, end_pos, radius)
