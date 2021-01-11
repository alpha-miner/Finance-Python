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
from collections import deque
import numpy as np
from PyFin.Math.Accumulators.impl import (
    Deque,
    DiffDeque
)


class TestAccumulatorImpl(unittest.TestCase):

    def testDequeDeepCopy(self):
        benchmark_deque = Deque(5)

        copied_deque = copy.deepcopy(benchmark_deque)

        self.assertEqual(copied_deque, benchmark_deque)

    def testDequePickle(self):
        benchmark_deque = Deque(5)

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(benchmark_deque, f)

        with open(f.name, 'rb') as f2:
            pickled_deque = pickle.load(f2)
            self.assertEqual(benchmark_deque, pickled_deque)

        os.unlink(f.name)

    def testDequeSum(self):
        deque = Deque(5)
        deque.dumps([1., 2., 3., 4., 5., 6.])
        self.assertEqual(deque.sum(), 20.)

    def testDequeIdx(self):
        deque1 = deque(maxlen=10)
        deque2 = Deque(10)

        values = np.random.randn(1000)
        for v in values:
            deque1.append(v)
            deque2.dumps([v])

            max_val = max(deque1)
            expected_idx = np.where(np.array(deque1) == max_val)[0][0]
            caclulated_idx = deque2.idx(max_val)
            self.assertEqual(expected_idx, caclulated_idx)

    def testDiffDequeDump(self):
        deque = DiffDeque(10)
        values = [1, 2, 3, 4, 5]
        stamps = [1, 7, 9, 13, 26]

        for i, (v, s) in enumerate(zip(values, stamps)):
            ret_values = deque.dump(v, s)
            if i in (0, 1, 2):
                self.assertTrue(not ret_values)
            elif i == 3:
                self.assertEqual(ret_values, [1])
            elif i == 4:
                self.assertEqual(ret_values, [2, 3, 4])

    def testDiffDequeSum(self):
        deque = DiffDeque(10)
        values = [1, 2, 3, 4, 5]
        stamps = [1, 7, 9, 13, 26]

        for i, (v, s) in enumerate(zip(values, stamps)):
            deque.dump(v, s)
            if i == 0:
                self.assertTrue(deque.sum(), 1)
            elif i == 1:
                self.assertTrue(deque.sum(), 3)
            elif i == 2:
                self.assertTrue(deque.sum(), 6)
            elif i == 3:
                self.assertTrue(deque.sum(), 9)
            elif i == 4:
                self.assertTrue(deque.sum(), 5)


