
import pygame

class Cell():

    SIZE = 50
    SIZE_LIMIT_MIN = 2      # 1px for wall, 1px for cell

    BG_COLOR         = pygame.Color('black')
    WALL_COLOR       = pygame.Color('black')
    VISITED_COLOR    = pygame.Color('grey')
    HIGHTLIGHT_COLOR = pygame.Color('cyan')
    STACKED_COLOR    = pygame.Color('purple')

    def __init__(self, x, y):
        self._x = x
        self._y = y
        self._pos = (self._x * Cell.SIZE, self._y * Cell.SIZE)

        self._visited = False
        self._stacked = False

        self._walls = {cardinality:True for cardinality in 'NSEW'}

        self._surface = pygame.Surface((Cell.SIZE, Cell.SIZE))
        self._surface_updated = False
        self._draw_cell()

    def __hash__(self):
        return hash((self._x, self._y))

    def __eq__(self, other):
        if other is None:
            return False
        return (self._x, self._y) == (other._x, other._y)

    def __str__(self):
        return f'{self.__class__.__name__}({self._x}, {self._y})'

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def need_redraw(self):
        return self._surface_updated

    @property
    def is_visited(self):
        return self._visited

    def is_wall(self, cardinality):
        return self._walls[cardinality]

    def _draw_cell(self):
        color = Cell.BG_COLOR
        if self._visited:
            color = Cell.VISITED_COLOR
        if self._stacked:
            color = Cell.STACKED_COLOR
        self._surface.fill(color)

        w, h = self._surface.get_size()
        thickness = 1

        for cardinality, has_wall in self._walls.items():
            if has_wall:
                if cardinality == 'N':
                    pygame.draw.line(self._surface, Cell.WALL_COLOR, (0, 0), (w - 1, 0), thickness)
                if cardinality == 'S':
                    pygame.draw.line(self._surface, Cell.WALL_COLOR, (0, h), (w - 1, h), thickness)
                if cardinality == 'E':
                    pygame.draw.line(self._surface, Cell.WALL_COLOR, (w, 0), (w, h - 1), thickness)
                if cardinality == 'W':
                    pygame.draw.line(self._surface, Cell.WALL_COLOR, (0, 0), (0, h - 1), thickness)

        self._surface_updated = True

    def visit(self):
        self._visited = True
        self._draw_cell()

    def stack(self):
        self._stacked = True
        self._draw_cell()

    def unstack(self):
        self._stacked = False
        self._draw_cell()

    def remove_wall(self, cardinality):
        assert(cardinality in 'NSEW')
        self._walls[cardinality] = False
        self._draw_cell()

    def draw(self, screen):
        if not self.need_redraw:
            return

        screen.blit(self._surface, self._pos)
        self._surface_updated = False

    def hightlight(self, screen):
        screen.fill(self.HIGHTLIGHT_COLOR, pygame.Rect(self._pos, (Cell.SIZE, Cell.SIZE)))
