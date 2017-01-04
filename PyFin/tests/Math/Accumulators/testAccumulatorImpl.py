# -*- coding: utf-8 -*-
u"""
Created on 2017-1-4

@author: cheng.li
"""

import unittest
import copy
import tempfile
import pickle
import os
from PyFin.Math.Accumulators.impl import Deque


class TestAccumulatorImpl(unittest.TestCase):

    def testDequeDeepCopy(self):
        benchmark_deque = Deque(5)
        benchmark_deque.dump(2.)

        copied_deque = copy.deepcopy(benchmark_deque)

        self.assertEqual(copied_deque, benchmark_deque)

    def testDequePickle(self):
        benchmark_deque = Deque(5)
        benchmark_deque.dump(2.)

        f = tempfile.NamedTemporaryFile('w+b', delete=False)
        pickle.dump(benchmark_deque, f)
        f.close()

        with open(f.name, 'rb') as f2:
            pickled_deque = pickle.load(f2)
            self.assertEqual(benchmark_deque, pickled_deque)

        os.unlink(f.name)
