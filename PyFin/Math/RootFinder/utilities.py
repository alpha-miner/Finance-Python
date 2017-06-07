# -*- coding: utf-8 -*-
u"""
Created on 2017-6-7

@author: cheng.li
"""

from math import fabs


class Converged(object):

    def __init__(self, x_tol, f_tol):

        self.x_tol = x_tol
        self.f_tol = f_tol

    def check_converge(self, root_finder, e):
        root_finder.putY(e)
        return fabs(e) < self.f_tol or root_finder.bracketWidth() < self.x_tol
