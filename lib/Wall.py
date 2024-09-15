
import pygame
from pygame.math import Vector2 as Vec
import random

class Wall():

    COLOR = (255, 255, 255)

    def __init__(self, screen_size=(1, 1), a=None, b=None):
        w, h = screen_size

        if a == None:
            self._a = Vec(random.uniform(0, w - 1), random.uniform(0, h - 1))
        else:
            self._a = Vec(a)

        if b == None:
            self._b = Vec(random.uniform(0, w - 1), random.uniform(0, h - 1))
        else:
            self._b = Vec(b)

    @property
    def a(self):
        return self._a

    @property
    def b(self):
        return self._b

    def draw_map(self, screen):
        pygame.draw.line(screen, Wall.COLOR, self._a, self._b, 1)

    def draw_view(self, screen):
        pass
