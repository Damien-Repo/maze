
import pygame

class Cell():

    SIZE = 50

    BG_COLOR         = (  0,   0,   0)
    WALL_COLOR       = (  0,   0,   0)
    VISITED_COLOR    = (127, 127, 127)
    HIGHTLIGHT_COLOR = (  0, 180, 180)
    STACKED_COLOR    = ( 42,   0,  42)

    def __init__(self, x, y):
        self._x = x
        self._y = y
        self._pos = (self._x * Cell.SIZE, self._y * Cell.SIZE)

        self._visited = False
        self._stacked = False

        self._walls = {cardinality:True for cardinality in 'NSEW'}

        self._surface = pygame.Surface((Cell.SIZE, Cell.SIZE))
        self._draw_cell()

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def is_visited(self):
        return self._visited

    def _draw_cell(self):
        color = Cell.BG_COLOR
        if self._visited:
            color = Cell.VISITED_COLOR
        if self._stacked:
            color = Cell.STACKED_COLOR
        self._surface.fill(color)

        w, h = self._surface.get_size()
        thickness = 1

        for C,v in self._walls.items():
            if v == True:
                if C == 'N':
                    pygame.draw.line(self._surface, Cell.WALL_COLOR, (0, 0), (w - 1, 0), thickness)
                if C == 'S':
                    pygame.draw.line(self._surface, Cell.WALL_COLOR, (0, h), (w - 1, h), thickness)
                if C == 'E':
                    pygame.draw.line(self._surface, Cell.WALL_COLOR, (w, 0), (w, h - 1), thickness)
                if C == 'W':
                    pygame.draw.line(self._surface, Cell.WALL_COLOR, (0, 0), (0, h - 1), thickness)

    def visit(self):
        self._visited = True
        self._draw_cell()

    def stack(self):
        self._stacked = True
        self._draw_cell()

    def unstack(self):
        self._stacked = False
        self._draw_cell()

    def __str__(self):
        return 'Cell(%d, %d)' % (self._x, self._y)

    def remove_wall(self, cardinality):
        assert cardinality in 'NSEW'
        self._walls[cardinality] = False
        self._draw_cell()

    def draw(self, screen):
        screen.blit(self._surface, self._pos)

    def hightlight(self, screen):
        surf = self._surface.copy()
        surf.fill(Cell.HIGHTLIGHT_COLOR)
        screen.blit(surf, self._pos)
