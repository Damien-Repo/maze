
import pygame
from pygame.math import Vector2 as Vec
import numpy as np
import math

class Ray():

    COLOR = (0, 255, 0, 100)

    def __init__(self, pos, angle):
        self._pos = pos
        self.rotate(angle)

        self._angle = angle

    @property
    def heading(self):
        return self._angle

    def rotate(self, angle):
        self._dir = Vec(0, -1).rotate(angle)

    def cast(self, wall):
        '''
        Source: https://en.wikipedia.org/wiki/Line-line_intersection
        '''
        x1 = wall.a.x
        y1 = wall.a.y
        x2 = wall.b.x
        y2 = wall.b.y

        x3 = self._pos.x
        y3 = self._pos.y
        x4 = self._pos.x + self._dir.x
        y4 = self._pos.y + self._dir.y

        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if den == 0:
            return

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den
        if t > 0 and t < 1 and u > 0:
            pt = Vec()
            pt.x = x1 + t * (x2 - x1)
            pt.y = y1 + t * (y2 - y1)
            return pt
        else:
            return

    def draw(self, screen):
        start = (int(self._pos.x), int(self._pos.y))
        end_vec = self._pos + self._dir * 10
        end = (int(end_vec.x), int(end_vec.y))
        pygame.draw.line(screen, Ray.COLOR, start, end, 1)


class Player():

    COLOR = (0, 0, 255)
    SPEED = 2.5
    ROTATION_SPEED = 2.5

    def __init__(self, pos, fov=66):
        self._fov = fov

        self._pos = Vec(pos)

        self._heading = 0
        self._rotation = 0
        self._speed = 0

        self._rays = [Ray(self._pos, angle) for angle in range(-self._fov // 2, self._fov // 2)]
        self._rays_view = []

    def move(self, forward, add=True):
        self._speed = Player.SPEED
        if not forward: self._speed *= -1
        if not add: self._speed = 0

    def rotate(self, turn_left, add=True):
        turn = Player.ROTATION_SPEED
        if turn_left: turn *= -1
        if not add: turn *= 0
        self._rotation = turn

    def event(self, event):
        if event.type != pygame.KEYDOWN and event.type != pygame.KEYUP:
            return

        if event.key == pygame.K_UP:
            self.move(True, event.type == pygame.KEYDOWN)
        if event.key == pygame.K_DOWN:
            self.move(False, event.type == pygame.KEYDOWN)
        if event.key == pygame.K_LEFT:
            self.rotate(True, event.type == pygame.KEYDOWN)
        if event.key == pygame.K_RIGHT:
            self.rotate(False, event.type == pygame.KEYDOWN)

    def _update_rays(self):
        if self._rotation == 0:
            return

        i = 0
        for angle in range(-self._fov // 2, self._fov // 2):
            self._rays[i].rotate(angle + self._heading)
            i += 1

    def _rays_cast(self, walls):
        self._rays_view = [(None, None) for _ in range(-self._fov // 2, self._fov // 2)]

        for i,ray in enumerate(self._rays):
            closest = None
            dist_min = float('inf')
            for wall in walls:
                pt = ray.cast(wall)
                if pt != None:
                    d = self._pos.distance_to(pt)
                    #a = ray.heading #- self._heading
                    #d *= math.cos(a)
                    if d < dist_min:
                        dist_min = d
                        closest = pt

            if closest != None:
                self._rays_view[i] = (closest, dist_min)

    def update(self, walls):
        if self._rotation != 0:
            self._heading += self._rotation

        if self._speed != 0:
            vel = Vec(0, -1).rotate(self._heading)
            vel.scale_to_length(self._speed)
            self._pos += vel

        self._update_rays()
        self._rays_cast(walls)

    def draw_map(self, screen):
        for pt,_ in self._rays_view:
            if pt == None: continue
            pygame.draw.line(screen, (255, 255, 255), self._pos, pt, 1)

        pos = (int(self._pos.x), int(self._pos.y))
        pygame.draw.circle(screen, Player.COLOR, pos, 5, 1)

    def draw_view(self, screen):
        w, h = screen.get_size()
        w_px = w // len(self._rays_view)
        for i,(pt,d) in enumerate(self._rays_view):
            if pt == None: continue
            b = np.interp(d**2, [0, w**2], [255, 0])        #//TEMP penser a rename 'b'
            wall_h = np.interp(d, [0, w], [h, 0])
            pos_start = (i * w_px + w_px // 2, h // 2 - wall_h // 2)
            pos_end = (i * w_px + w_px // 2, h // 2 + wall_h // 2)
            pygame.draw.line(screen, (b, b, b), pos_start, pos_end, w_px)
