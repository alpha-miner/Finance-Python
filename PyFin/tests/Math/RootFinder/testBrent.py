# -*- coding: utf-8 -*-
u"""
Created on 2017-6-7

@author: cheng.li
"""

import unittest
from PyFin.Math.RootFinder import Converged
from PyFin.Math.RootFinder import BracketedBrent
from PyFin.Math.RootFinder import Brent


def root_func(x):
    return x * x - 1.


class TestBrent(unittest.TestCase):

    def testBracketedBrent(self):
        converge = Converged(1e-8, 1e-8)

        low = 0., root_func(0.)
        high = 2., root_func(2.)

        brent = BracketedBrent(1e-8, low, high)
        iterations = 0

        while True and iterations < 100:
            iterations += 1
            x = brent.nextX()
            if converge.check_converge(brent, root_func(x)):
                break

        self.assertAlmostEqual(x, 1.)

    def testBracketedBrentNotBracketed(self):
        low = 0., 1.
        high = 2., 1.

        with self.assertRaises(ValueError):
            _ = BracketedBrent(1e-8, low, high)

    def testBrent(self):
        converge = Converged(1e-8, 1e-8)

        brent = Brent(1.5)
        iterations = 0

        while True and iterations < 100:
            iterations += 1
            x = brent.nextX()
            if converge.check_converge(brent, root_func(x)):
                break

        self.assertAlmostEqual(x, 1.)

        brent = Brent(-1.5)
        iterations = 0

        while True and iterations < 100:
            iterations += 1
            x = brent.nextX()
            if converge.check_converge(brent, root_func(x)):
                break

        self.assertAlmostEqual(x, -1.)


if __name__ == '__main__':
    unittest.main()
