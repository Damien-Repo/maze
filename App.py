#!/usr/bin/env python

import os
from os.path import exists as file_exists
from datetime import datetime
import json

import argparse
import sys
import re

import pygame

from lib.Maze import Maze
from lib.Map import Map
from lib.Pathfinder import Pathfinder


class App():

    BG_COLOR = pygame.Color(0, 0, 0, 0)

    USEREVENT_RESTART = pygame.USEREVENT + 1
    RESTART_FREEZE_TIME = 3     # in sec

    FPS = 100

    def __init__(self, cols=None, rows=None, start_pos=None, end_pos=None, dump=None, save_generated_maze=False, load_generated_maze=None):
        assert(cols is None or cols > 0)
        assert(rows is None or rows > 0)

        self._running = False
        self._cur_update_step = None

        self._map = None
        self._maze = None
        self._pathfinder = None

        self._cols = cols
        self._rows = rows

        self._init_pygame()

        self._save_generated_maze = save_generated_maze
        self._loaded_data = None
        if load_generated_maze is not None:
            self._loaded_data = json.load(load_generated_maze)

        self._start_pos = start_pos
        self._end_pos = end_pos

        self._multiple_update_counter = 1

        self._dump = dump
        self._dump_uuid = None

        self._debug_mode = False

    @classmethod
    def generate_dump_uuid(cls):
        return datetime.now().strftime('%Y%m%d%H%M%S')

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

        self._clock = pygame.time.Clock()

        print('''
=========================
Controls:

  ESCAPE or 'Q' => Exit
  'R'           => Restart
  'S'           => To save the current map
  'D'           => Toggle debug mode during pathfinding
  '+' / '-'     => Increase/Decrease by 10 the number of updates per frame
=========================
        ''')

    @property
    def window_title(self):
        out = f'Maze - FPS: {self._clock.get_fps():.2f}'
        if self._maze is not None and not self._maze.was_generated:
            out += f' (Generating {self._maze.progression:.2f}%)'
        if self._pathfinder is not None and not self._pathfinder.path_found():
            out += f' (Finding path length: {len(self._pathfinder)} cells)'
        if self._multiple_update_counter > 1:
            out += f' x{self._multiple_update_counter}'
        if self._debug_mode:
            out += ' (DEBUG MODE)'
        return out

    def _init_map(self):
        self._map = Map(self._screen_map.get_size(), self._cols, self._rows, self._loaded_data)

        if self._loaded_data is not None:
            self._map.draw_all_cells(self._screen_map)

    def _init_maze(self):
        assert(self._map is not None)
        self._maze = Maze(self._map)

    def _init_pathfinder(self):
        assert(self._map is not None)
        assert(self._start_pos is None or (0 <= self._start_pos[0] < self._map.cols and 0 <= self._start_pos[1] < self._map.rows))
        assert(self._end_pos is None or (0 <= self._end_pos[0] < self._map.cols and 0 <= self._end_pos[1] < self._map.rows))
        self._pathfinder = Pathfinder(self._map, self._start_pos, self._end_pos)

    def _restart(self):
        pygame.time.set_timer(self.USEREVENT_RESTART, 0)        # Remove restart event

        self._map = None
        self._maze = None
        self._pathfinder = None

        self._screen_map.fill(self.BG_COLOR)
        self._screen_path.fill(self.BG_COLOR)

        self._dump_uuid = self.generate_dump_uuid()

        self._cur_update_step = 0

    def events(self):
        for event in pygame.event.get():
            if event == pygame.NOEVENT:
                continue

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self._running = False
                elif event.key == pygame.K_r:
                    self._restart()
                elif event.key == pygame.K_s:
                    self._update_step_4_save_maze(force=True)
                elif event.key == pygame.K_d:
                    self._debug_mode = not self._debug_mode
                elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS):
                    self._multiple_update_counter += 10
                    self._multiple_update_counter = min(self._multiple_update_counter, 1000)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self._multiple_update_counter -= 10
                    self._multiple_update_counter = max(self._multiple_update_counter, 1)
                continue

            if event.type == self.USEREVENT_RESTART:
                self._restart()
                continue

    def _dump_screen(self, filename):
        if not self._dump:
            return

        filename = f'{self._dump_uuid}_{filename}'
        if file_exists(filename):
            return

        pygame.image.save(self._screen, filename)

    def _update_step_1_init_map(self):
        assert(self._map is None)

        self._init_map()

        return True

    def _update_step_2_init_maze(self):
        assert(self._maze is None)

        self._init_maze()

        return True

    def _update_step_3_generate_maze(self):
        assert(not self._maze.was_generated)

        if int(self._maze.progression) in (25, 50, 75):
            self._dump_screen(f'maze_{int(self._maze.progression)}%_generated.png')

        self._maze.update(multiple_update_counter=self._multiple_update_counter)

        return self._maze.was_generated

    def _update_step_4_save_maze(self, force=False):
        if self._save_generated_maze or force:
            with open(f'{self._dump_uuid}_maze_{self._map.cols}x{self._map.rows}.json', 'w', encoding='utf-8') as f:
                json.dump(self._map.save(), f)

        return True

    def _update_step_5_init_pathfinder(self):
        assert(self._pathfinder is None)

        self._dump_screen('maze_generated.png')
        self._init_pathfinder()

        return True

    def _update_step_6_find_path(self):
        assert(not self._pathfinder.path_found())

        self._pathfinder.update(multiple_update_counter=self._multiple_update_counter)

        return self._pathfinder.path_found()

    def _update_step_7_render_full_path(self):
        return self._pathfinder.is_final_path_full_rendered

    def _update_step_8_launch_restart(self):
        self._dump_screen('path_found.png')

        pygame.time.set_timer(self.USEREVENT_RESTART, self.RESTART_FREEZE_TIME * 1000)

        return True

    def _update_step_9_wait_restart(self):
        return None

    ALL_UPDATE_STEP_FUNCS = [
        '_update_step_1_init_map',
        '_update_step_2_init_maze',
        '_update_step_3_generate_maze',
        '_update_step_4_save_maze',
        '_update_step_5_init_pathfinder',
        '_update_step_6_find_path',
        '_update_step_7_render_full_path',
        '_update_step_8_launch_restart',
        '_update_step_9_wait_restart',
    ]

    def update(self):
        assert(self._cur_update_step is not None)

        update_func = getattr(self, self.ALL_UPDATE_STEP_FUNCS[self._cur_update_step], None)
        assert(update_func is not None)

        if update_func():
            self._cur_update_step += 1
            if self._cur_update_step >= len(self.ALL_UPDATE_STEP_FUNCS):
                self._cur_update_step = 0


    def draw(self):
        if self._pathfinder is None:
            if self._map is not None:
                self._map.draw(self._screen_map)

            if self._maze is not None:
                self._maze.draw(self._screen_map)
        else:
            if not self._pathfinder.path_found():
                self._screen_path.fill(self.BG_COLOR)
                self._pathfinder.draw(self._screen_path, debug=self._debug_mode)
            else:
                self._pathfinder.draw_full_path(self._screen_path)

        self._screen.blit(self._screen_map, (0, 0))
        self._screen.blit(self._screen_path, (0, 0))

        pygame.display.update()

    def run(self):
        self._running = True

        self._restart()

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
    parser.add_argument('--save', '--save-maze',
                        action='store_true',
                        dest='save_generated_maze',
                        help='save the generated maze')
    parser.add_argument('--load', '--load-maze',
                        type=argparse.FileType('r'),
                        dest='load_generated_maze',
                        metavar='load_generated_maze',
                        help='load a pre generated maze')
    args = parser.parse_args()

    app_params = {
        'cols': None,
        'rows': None,
        'start_pos': None,
        'end_pos': None,
        'dump': None,
        'save_generated_maze': None,
        'load_generated_maze': None,
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

    app_params['save_generated_maze'] = args.save_generated_maze
    app_params['load_generated_maze'] = args.load_generated_maze

    a = App(**app_params)
    a.run()
    print('END APP')        #//TEMP
