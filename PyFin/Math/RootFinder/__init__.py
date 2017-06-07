# -*- coding: utf-8 -*-
u"""
Created on 2017-6-7

@author: cheng.li

This package offers the ability to
find the root of a single valued equation.
The implementation is greatly inspired by:

Derivatives Algorithms, Volume 1: Bones, 2nd ed., Tom Hyer, World Scientific, 2016.

"""

from PyFin.Math.RootFinder.Brent import BracketedBrent
from PyFin.Math.RootFinder.Brent import Brent

from PyFin.Math.RootFinder.utilities import Converged


__all__ = ['BracketedBrent',
           'Brent',
           'Converged']
