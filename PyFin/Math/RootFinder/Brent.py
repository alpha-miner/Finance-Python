# -*- coding: utf-8 -*-
u"""
Created on 2017-6-7

@author: cheng.li
"""

from math import exp
from math import fabs
from numpy import inf
from PyFin.Utilities.Asserts import pyFinAssert
from PyFin.Math.RootFinder.RootFinderBase import RootFinder


class BracketedBrent(RootFinder):

    def __init__(self, tol, low=None, high=None):
        self.tol = tol
        self.a = None
        self.b = None
        self.c = None
        self.bisect = None
        self.d = None

        if low and high:
            self.initialize(low, high)

    def initialize(self, low, high):
        self.a = low
        self.b = high

        pyFinAssert(self.a[1] * self.b[1] <= 0., ValueError, 'root is not bracketed')

        if fabs(self.a[1]) < fabs(self.b[1]):
            self.a, self.b = self.b, self.a

        self.c = self.a
        self.bisect = True
        self.d = 0

    def bracketWidth(self):
        return fabs(self.a[0] - self.b[0])

    def putY(self, y):
        s = self.d
        self.d = self.c[0]
        self.c = self.b

        if y * self.a[1] > 0.:
            self.a = s, y
        else:
            self.b = s, y

        if fabs(self.a[1]) < fabs(self.b[1]):
            self.a, self.b = self.b, self.a

    def nextX(self):
        if self.c[1] != self.a[1] and self.c[1] != self.b[1]:
            # inverse quadratic interpolation
            s = self.a[0] * self.b[1] * self.c[1] / ((self.a[1] - self.b[1]) * (self.a[1] - self.c[1])) \
                + self.b[0] * self.a[1] * self.c[1] / ((self.b[1] - self.a[1]) * (self.b[1] - self.c[1])) \
                + self.c[0] * self.a[1] * self.b[1] / ((self.c[1] - self.a[1]) * (self.c[1] - self.b[1]))
        else:
            s = (self.a[0] * self.b[1] - self.b[0] * self.a[1]) / (self.b[1] - self.a[1])

        c_dist = fabs(self.c[0] - self.b[0] if self.bisect else self.d)
        self.bisect = (s - self.b[0]) * (s - 0.75 * self.a[0] - 0.25 * self.b[0]) >= 0. \
                      or fabs(s - self.b[0]) > 0.5 * c_dist \
                      or c_dist < self.tol

        if self.bisect:
            s = 0.5 * (self.a[0] + self.b[0])

        self.d = s
        return s


class Brent(RootFinder):

    expansion = exp(1.0)

    def __init__(self, guess, tol=1e-8, step_size=0.):
        self.phase = 'init'
        self.increasing = True
        self.step_size = step_size if step_size > 0. else 0.1 * max(0.01, fabs(guess))
        self.trial_x = guess
        self.known_points = inf, inf
        self.engine = BracketedBrent(tol)

    def nextX(self):
        return self.engine.nextX() if self.phase == 'bracketed' else self.trial_x

    def putY(self, y):
        if self.phase == 'init':
            self.known_points = self.trial_x, y
            self.trial_x += self.step_size * (1. if self.increasing else -1.) * (1. if y < 0. else -1.)
            self.phase = 'hunt'
        elif self.phase == 'bracketed':
            self.engine.putY(y)
        elif self.phase == 'hunt':
            if y * self.known_points[1] <= 0.:
                self.engine.initialize(self.known_points, (self.trial_x, y))
                self.phase = 'bracketed'
            else:
                if fabs(y) > fabs(self.known_points[1]):
                    self.increasing = not self.increasing
                else:
                    self.known_points = self.trial_x, y

                self.step_size *= self.expansion
                self.trial_x = self.known_points[0] \
                               + (1. if self.increasing else -1.) \
                                 * (1. if self.known_points[1] < 0. else -1.) * self.step_size

    def bracketWidth(self):
        return self.engine.bracketWidth() if self.phase == 'bracketed' else inf
