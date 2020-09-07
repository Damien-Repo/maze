#!/usr/bin/env python

import os
import pygame

from Maze import Maze

class App():

    W = 900
    H = 900

    BG_COLOR =    (  0,   0, 0)

    def __init__(self, width=None, height=None):
        if width == None: width = App.W
        if height == None: height = App.H

        self._init_pygame(width, height)
        self._restart()

    def _init_pygame(self, width, height):
        self._w = width
        self._h = height

        pygame.init()
        info = pygame.display.Info()
        os.environ['SDL_VIDEO_WINDOW_POS'] = '%d,%d' % ((info.current_w - self._w) / 2, 0)
        self._screen = pygame.display.set_mode((self._w, self._h))
        pygame.display.set_caption('--- Maze ---')

        self._clock = pygame.time.Clock()

        print('''
=========================
Commands:

  ESCAPE or 'q'       => Exit
  'r'                 => Restart
=========================
        ''')

    def _init_maze(self):
        self._maze = Maze((self._w, self._h))

    def _restart(self):
        self._init_maze()

    @property
    def game_end(self):
        return False    #//TEMP

    def events(self):
        for event in pygame.event.get():
            if event != pygame.NOEVENT:
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q):
                    self._running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self._restart()
                else:
                    pass

    def update(self):
        if self.game_end:
            return

        self._maze.update()

    def draw(self):
        self._screen.fill(App.BG_COLOR)

        self._maze.draw(self._screen)

        pygame.display.update()

    def run(self):
        self._running = True
        while self._running:
            self._clock.tick(60)

            self.events()
            self.update()
            self.draw()


if __name__ == '__main__':
    a = App()
    a.run()
