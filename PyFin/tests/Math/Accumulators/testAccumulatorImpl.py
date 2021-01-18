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
    DiffDeque,
    UniqueDiffDeque
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

    def testDiffDequeDeepCopy(self):
        benchmark_deque = DiffDeque(5, closed="left")
        copied_deque = copy.deepcopy(benchmark_deque)
        self.assertEqual(copied_deque, benchmark_deque)

    def testDiffDequeSum(self):
        deque = DiffDeque(10)
        values = [1, 2, 3, 4, 5]
        stamps = [1, 7, 9, 13, 26]

        deque.dumps(values, stamps)
        self.assertEqual(deque.sum(), 5)

    def testDiffDequeWithLeftClosedSum(self):
        deque = DiffDeque(10, closed="left")

        values = [1, 2, 3, 4, 5]
        stamps = [1, 7, 9, 16, 26]

        deque.dumps(values, stamps)
        self.assertEqual(deque.sum(), 4)

    def testDiffDequeWithBothClosedSum(self):
        deque = DiffDeque(10, closed="both")

        values = [1, 2, 3, 4, 5]
        stamps = [1, 7, 9, 16, 26]

        deque.dumps(values, stamps)
        self.assertEqual(deque.sum(), 9)

    def testDiffDequeWithNeitherClosedSum(self):
        deque = DiffDeque(10, closed="neither")

        values = [1, 2, 3, 4, 5]
        stamps = [1, 7, 9, 16, 26]

        deque.dumps(values, stamps)
        self.assertEqual(deque.sum(), 0)

    def testUniqueDiffDequeDeepCopy(self):
        benchmark_deque = UniqueDiffDeque(5, closed="left")
        copied_deque = copy.deepcopy(benchmark_deque)
        self.assertEqual(copied_deque, benchmark_deque)

    def testUniqueDiffDequeSum(self):
        deque = UniqueDiffDeque(10)
        values = [2, 2, 3, 5, 5]
        stamps = [1, 7, 20, 22, 26]

        deque.dumps(values, stamps)
        self.assertEqual(deque.sum(), 8)

    def testUniqueDiffDequeWithLeftClosedSum(self):
        deque = UniqueDiffDeque(10, closed="left")

        values = [2, 2, 5, 5, 5]
        stamps = [1, 16, 20, 22, 26]

        deque.dumps(values, stamps)
        self.assertEqual(deque.sum(), 7)

    def testUniqueDiffDequeWithBothClosedSum(self):
        deque = UniqueDiffDeque(10, closed="both")

        values = [2, 2, 5, 5, 7]
        stamps = [1, 16, 20, 22, 26]

        deque.dumps(values, stamps)
        self.assertEqual(deque.sum(), 14)

    def testUniqueDiffDequeWithNeitherClosedSum(self):
        deque = UniqueDiffDeque(10, closed="neither")

        values = [2, 2, 5, 5, 7]
        stamps = [1, 16, 20, 22, 26]

        deque.dumps(values, stamps)
        self.assertEqual(deque.sum(), 5)




