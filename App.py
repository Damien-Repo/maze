#!/usr/bin/env python

import os

import argparse
import sys
import re

import pygame

from lib.Maze import Maze
from lib.Map import Map
from lib.Pathfinder import Pathfinder


class App():

    BG_COLOR = pygame.Color(0, 0, 0, 0)

    RESTART_FREEZE_TIME = 2     # in sec

    FPS = 100

    def __init__(self, cols=None, rows=None, start_pos=None, end_pos=None, dump=None):
        assert(cols is None or cols > 0)
        assert(rows is None or rows > 0)

        self._running = False

        self._map = None
        self._maze = None
        self._pathfinder = None

        self._maze_progression = None

        self._cols = cols
        self._rows = rows

        self._init_pygame()

        assert(start_pos is None or (0 <= start_pos[0] < self._cols and 0 <= start_pos[1] < self._rows))
        assert(end_pos is None or (0 <= end_pos[0] < self._cols and 0 <= end_pos[1] < self._rows))
        self._start_pos = start_pos
        self._end_pos = end_pos

        self._dump = dump

    def _init_pygame(self):
        pygame.init()

        info = pygame.display.Info()
        screen_w, screen_h = (info.current_w - 10, info.current_h - 110)
        os.environ['SDL_VIDEO_WINDOW_POS'] = f'{(info.current_w - screen_w) // 2},0'
        pygame.display.set_caption('--- Maze ---')

        self._screen = pygame.display.set_mode((screen_w, screen_h))
        self._screen_map = self._screen.copy()
        self._screen_path = self._screen.copy().convert_alpha()
        self._screen_path.fill(self.BG_COLOR)

        if self._cols is None:
            self._cols = screen_w // 10
        if self._rows is None:
            self._rows = screen_h // 10

        self._clock = pygame.time.Clock()

        print('''
=========================
Controls:

  ESCAPE or 'Q' => Exit
  'R'           => Restart
=========================
        ''')

    @property
    def window_title(self):
        out = f'Maze - FPS: {self._clock.get_fps():.2f}'
        if self._maze is not None and self._maze.progression < 100.0:
            out += f' (Generating {self._maze.progression:.2f}%)'
        return out

    def _init_map(self):
        self._map = Map(self._screen_map, self._cols, self._rows)

    def _init_maze(self):
        assert(self._map is not None)
        self._maze = Maze(self._map)

    def _init_pathfinder(self):
        assert(self._map is not None)
        self._pathfinder = Pathfinder(self._map, self._start_pos, self._end_pos)

    def _restart(self, wait=False):
        if wait:
            pygame.time.wait(int(self.RESTART_FREEZE_TIME * 1000))

        self._map = None
        self._maze = None
        self._pathfinder = None

        self._screen_map.fill(self.BG_COLOR)
        self._screen_path.fill(self.BG_COLOR)

    def events(self):
        for event in pygame.event.get():
            if event != pygame.NOEVENT:
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q):
                    self._running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self._restart()

    def update(self):
        if self._map is None:
            self._init_map()
            return

        if self._maze is None:
            self._init_maze()
            return

        if not self._maze.was_generated:
            if self._dump and self._maze.progression == 50.0:
                pygame.image.save(self._screen, 'maze_half_generated.png')
            self._maze.update()
            return

        if self._pathfinder is None:
            if self._dump:
                pygame.image.save(self._screen, 'maze_generated.png')
            self._init_pathfinder()
            return

        if not self._pathfinder.path_found():
            self._pathfinder.update()
            return

        if not self._pathfinder.final_path_drawn():
            return

        if self._dump:
            pygame.image.save(self._screen, 'path_found.png')
        self._restart(wait=True)

    def draw(self):
        if self._pathfinder is None:
            if self._map is not None:
                self._map.draw(self._screen_map)

            if self._maze is not None:
                self._maze.draw(self._screen_map)
        else:
            self._screen_path.fill(self.BG_COLOR)
            self._pathfinder.draw(self._screen_path)

        self._screen.blit(self._screen_map, (0, 0))
        self._screen.blit(self._screen_path, (0, 0))

        pygame.display.update()

    def run(self):
        self._running = True
        while self._running:
            self._clock.tick(self.FPS)
            pygame.display.set_caption(self.window_title)

            self.events()
            self.update()
            self.draw()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    parser.add_argument('-d', '--dimensions', '--dims',
                        type=str,
                        dest='dims',
                        metavar='dims',
                        help='the dimensions of the map (cols, rows)')
    parser.add_argument('-s', '--start', '--start-pos',
                        type=str,
                        default=None,
                        dest='start_pos',
                        help='the start position for the pathfinder')
    parser.add_argument('-e', '--end', '--end-pos',
                        type=str,
                        default=None,
                        dest='end_pos',
                        help='the end position for the pathfinder')
    parser.add_argument('--dump',
                        action='store_true',
                        dest='dump',
                        help='dump the map at different stages of the generation process')
    args = parser.parse_args()

    app_params = {
        'cols': None,
        'rows': None,
        'start_pos': None,
        'end_pos': None,
        'dump': None,
    }

    if args.dims is not None:
        matched = re.match(r'[({\[]?(?P<cols>\d+)[,*x]\s?(?P<rows>\d+)[)}\]]?', args.dims)
        if matched is not None:
            app_params['cols'] = int(matched.groupdict().get('cols'))
            app_params['rows'] = int(matched.groupdict().get('rows'))

    if args.start_pos is not None:
        matched = re.match(r'[({\[]?(?P<pos_x>\d+)[, x]\s?(?P<pos_y>\d+)[)}\]]?', args.start_pos)
        if matched is not None:
            app_params['start_pos'] = (int(matched.groupdict().get('pos_x')), int(matched.groupdict().get('pos_y')))

    if args.end_pos is not None:
        matched = re.match(r'[({\[]?(?P<pos_x>\d+)[, x]\s?(?P<pos_y>\d+)[)}\]]?', args.end_pos)
        if matched is not None:
            app_params['end_pos'] = (int(matched.groupdict().get('pos_x')), int(matched.groupdict().get('pos_y')))

    app_params['dump'] = args.dump

    a = App(**app_params)
    a.run()
