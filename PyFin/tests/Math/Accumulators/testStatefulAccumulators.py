# -*- coding: utf-8 -*-
u"""
Created on 2015-7-16

@author: cheng.li
"""

import unittest
import csv
import os
import copy
import pickle
import tempfile
import math
import numpy as np
from collections import deque
from PyFin.Math.Accumulators import Current
from PyFin.Math.Accumulators import Latest
from PyFin.Math.Accumulators import Shift
from PyFin.Math.Accumulators import Delta
from PyFin.Math.Accumulators import Exp
from PyFin.Math.Accumulators import MovingMax
from PyFin.Math.Accumulators import MovingArgMax
from PyFin.Math.Accumulators import MovingMin
from PyFin.Math.Accumulators import MovingArgMin
from PyFin.Math.Accumulators import MovingRank
from PyFin.Math.Accumulators import MovingQuantile
from PyFin.Math.Accumulators import MovingAllTrue
from PyFin.Math.Accumulators import MovingAnyTrue
from PyFin.Math.Accumulators import MovingAverage
from PyFin.Math.Accumulators import MovingDecay
from PyFin.Math.Accumulators import MovingPositiveAverage
from PyFin.Math.Accumulators import MovingNegativeAverage
from PyFin.Math.Accumulators import MovingPositiveDifferenceAverage
from PyFin.Math.Accumulators import MovingNegativeDifferenceAverage
from PyFin.Math.Accumulators import MovingRSI
from PyFin.Math.Accumulators import MovingSum
from PyFin.Math.Accumulators import MovingCountedPositive
from PyFin.Math.Accumulators import MovingCountedNegative
from PyFin.Math.Accumulators import MovingVariance
from PyFin.Math.Accumulators import MovingStandardDeviation
from PyFin.Math.Accumulators import MovingNegativeVariance
from PyFin.Math.Accumulators import MovingCorrelation
from PyFin.Math.Accumulators import MovingProduct
from PyFin.Math.Accumulators import MACD
from PyFin.Math.Accumulators import XAverage
from PyFin.Math.Accumulators import MovingResidue


class TestStatefulAccumulators(unittest.TestCase):
    def setUp(self):
        np.random.seed(0)
        self.sample = np.random.randn(10000)

    def testCurrentValueHolderWithOtherValueHolder(self):
        test1 = Exp(Current('x'))
        test1.push({'x': 2.0})
        self.assertAlmostEqual(test1.value, math.exp(2.0))

        test1.push({'x': np.nan})
        self.assertTrue(math.isnan(test1.value))

    def testLatestValueHolderWithOtherValueHolder(self):
        test1 = Exp(Latest('x'))
        test1.push({'x': 2.0})
        self.assertAlmostEqual(test1.value, math.exp(2.0))

        test1.push({'x': np.nan})
        self.assertAlmostEqual(test1.value, math.exp(2.0))

    def testLatestValueHolderDeepCopy(self):

        latest = Latest('x')
        copied = copy.deepcopy(latest)

        self.assertTrue(math.isnan(copied.value))

        latest.push({'x': 1.})
        copied = copy.deepcopy(latest)
        self.assertTrue(copied.value, 1.)

    def testLatestValueHolderPickle(self):

        latest = Latest('x')

        f = tempfile.NamedTemporaryFile('w+b', delete=False)
        pickle.dump(latest, f)
        f.close()

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertTrue(math.isnan(pickled.result()))

        os.unlink(f.name)

        latest.push({'x': 1.})

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(latest, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertTrue(pickled.value, 1.)

        os.unlink(f.name)

    def testShiftValueHolder(self):
        ma = MovingAverage(10, 'close')

        with self.assertRaises(ValueError):
            _ = Shift(0, ma)

        test = Shift(1, ma)

        test.push(dict(close=2.0))
        ma.push(dict(close=2.0))
        previous = ma.result()
        test.push(dict(close=5.0))
        ma.push(dict(close=5.0))

        self.assertAlmostEqual(previous, test.result())

        previous = ma.result()
        test.push(dict(close=10.0))
        self.assertAlmostEqual(previous, test.result())

    def testDeltaValueHolder(self):
        ma = MovingAverage(10, 'close')

        with self.assertRaises(ValueError):
            _ = Delta(window=0, x=ma)

        test = Delta(2, ma)

        test.push(dict(close=2.0))
        ma.push(dict(close=2.0))
        p_previous = ma.result()
        test.push(dict(close=5.0))
        ma.push(dict(close=5.0))
        previous = ma.result()
        test.push(dict(close=7.0))
        ma.push(dict(close=7.0))

        self.assertAlmostEqual(ma.result() - p_previous, test.result())

        ma.push(dict(close=10.0))
        test.push(dict(close=10.0))
        self.assertAlmostEqual(ma.result() - previous, test.result())

    def testShiftValueHolderDeepcopy(self):
        ma = Latest('close')
        test = Shift(2, ma)

        test.push(dict(close=2.0))
        test.push(dict(close=3.0))
        test.push(dict(close=4.0))

        copied = copy.deepcopy(test)
        self.assertAlmostEqual(copied.value, test.value)

    def testShiftValueHolderPickle(self):
        ma = Latest('close')
        test = Shift(2, ma)

        test.push(dict(close=2.0))
        test.push(dict(close=3.0))
        test.push(dict(close=4.0))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

    def testMovingAverager(self):
        window = 120
        total = 2500

        mv = MovingAverage(window, 'z')
        runningSum = 0.0
        con = []
        for i in range(total):
            value = float(i)
            con.append(value)
            mv.push(dict(z=value))
            runningSum += value
            if i >= window:
                runningSum -= con[0]
                con = con[1:]

            if i >= window - 1:
                expected = runningSum / window
                calculated = mv.result()
                self.assertAlmostEqual(calculated, expected, 15, "at index {0:d}\n"
                                                                 "Average expected:   {1:f}\n"
                                                                 "Average calculated: {2:f}".format(i, expected,
                                                                                                    calculated))

    def testMovingDecay(self):
        window = 80
        total = 2500

        mv = MovingDecay(window, 'z')

        def calculate_decay(con, k):
            s = k - len(con) + 1
            c = (k + s) * (k - s + 1) / 2.
            sum_value = 0.
            for w in range(s, k + 1):
                i = w - s
                sum_value += w * con[i]
            return sum_value / c

        con = []
        for i in range(total):
            value = float(i)
            con.append(value)
            mv.push(dict(z=value))
            if i >= window:
                con = con[1:]

            if i >= 1:
                expected = calculate_decay(con, window)
                calculated = mv.result()
                self.assertAlmostEqual(calculated, expected, 15, "at index {0:d}\n"
                                                                 "Average expected:   {1:f}\n"
                                                                 "Average calculated: {2:f}".format(i, expected,
                                                                                                    calculated))

    def testMovingAverageDeepcopy(self):
        window = 20
        mv = MovingAverage(window, 'x')

        mv.push(dict(x=1.))
        mv.push(dict(x=2.))

        copied = copy.deepcopy(mv)
        self.assertAlmostEqual(copied.value, mv.value)

        for i in range(3, 40):
            mv.push(dict(x=float(i)))

        copied = copy.deepcopy(mv)
        self.assertAlmostEqual(copied.value, mv.value)

    def testMovingAveragePickle(self):
        window = 20
        mv = MovingAverage(window, 'x')

        mv.push(dict(x=1.))
        mv.push(dict(x=2.))

        f = tempfile.NamedTemporaryFile('w+b', delete=False)
        pickle.dump(mv, f)
        f.close()
        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(mv.value, pickled.value)
        os.unlink(f.name)

        for i in range(3, 40):
            mv.push(dict(x=float(i)))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(mv, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(mv.value, pickled.value)
        os.unlink(f.name)

    def testMovingPositiveAverager(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/averagepostiveandnegative_random.csv')

        window = 20
        mv = MovingPositiveAverage(window, 'z')
        self.assertAlmostEqual(mv.result(), 0.0, 15)

        with open(filePath, 'r') as fileHandler:
            reader = csv.reader(fileHandler)

            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mv.push(dict(z=float(row[1])))
                if i >= window:
                    expected = float(row[6])
                    calculated = mv.result()
                    self.assertAlmostEqual(calculated, expected, 8, "at index {0:d}\n"
                                                                    "Positive average expected:   {1:f}\n"
                                                                    "positive average calculated: {2:f}".format(i,
                                                                                                                expected,
                                                                                                                calculated))

    def testMovingPositiveAverageDeepcopy(self):
        mv = MovingPositiveAverage(3, 'x')
        mv.push(dict(x=1.))
        mv.push(dict(x=-1.))
        mv.push(dict(x=2.))

        copied = copy.deepcopy(mv)
        self.assertAlmostEqual(mv.value, copied.value)

        data = np.random.randn(20)

        for d in data:
            mv.push(dict(x=d))
            copied.push(dict(x=d))

            self.assertAlmostEqual(mv.value, copied.value)

    def testMovingPositiveAveragePickle(self):
        mv = MovingPositiveAverage(3, 'x')
        mv.push(dict(x=1.))
        mv.push(dict(x=-1.))
        mv.push(dict(x=2.))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(mv, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)

        self.assertAlmostEqual(mv.value, pickled.value)

        data = np.random.randn(20)

        for d in data:
            mv.push(dict(x=d))
            pickled.push(dict(x=d))

            self.assertAlmostEqual(mv.value, pickled.value)

    def testMovingPositiveDifferenceAverage(self):
        window = 10
        mv = MovingPositiveDifferenceAverage(window, 'x')

        last = self.sample[0]
        diff_list = []
        for i, value in enumerate(self.sample):
            mv.push(dict(x=value))
            diff = value - last
            if i > 0:
                diff_list.append(diff)
            last = value
            pos_list = np.maximum(diff_list[-window:], 0.)

            if i > 1:
                expected = 0. if np.isnan(np.mean(pos_list)) else np.mean(pos_list)
                calculated = mv.result()
                self.assertAlmostEqual(calculated, expected, 8, "at index {0:d}\n"
                                                                "Positive average expected:   {1:f}\n"
                                                                "positive average calculated: {2:f}".format(i,
                                                                                                            expected,
                                                                                                            calculated))

    def testMovingPositiveDifferenceAverageDeepcopy(self):
        mv = MovingPositiveDifferenceAverage(3, 'x')
        mv.push(dict(x=1.))
        mv.push(dict(x=-1.))
        mv.push(dict(x=2.))

        copied = copy.deepcopy(mv)
        self.assertAlmostEqual(mv.value, copied.value)

        data = np.random.randn(20)
        for d in data:
            mv.push(dict(x=d))
            copied.push(dict(x=d))

            self.assertAlmostEqual(mv.value, copied.value)

    def testMovingPositiveDifferenceAveragePickle(self):
        mv = MovingPositiveDifferenceAverage(3, 'x')
        mv.push(dict(x=1.))
        mv.push(dict(x=-1.))
        mv.push(dict(x=2.))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(mv, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)

        self.assertAlmostEqual(mv.value, pickled.value)

        data = np.random.randn(20)

        for d in data:
            mv.push(dict(x=d))
            pickled.push(dict(x=d))

            self.assertAlmostEqual(mv.value, pickled.value)

    def testMovingNegativeDifferenceAverage(self):
        window = 10
        mv = MovingNegativeDifferenceAverage(window, 'x')

        last = self.sample[0]
        diff_list = []
        for i, value in enumerate(self.sample):
            mv.push(dict(x=value))
            diff = value - last
            if i > 0:
                diff_list.append(diff)
            last = value
            neg_list = np.minimum(diff_list[-window:], 0.)

            if i > 0 and len(neg_list) > 0:
                expected = 0. if np.isnan(np.mean(neg_list)) else np.mean(neg_list)
                calculated = mv.result()
                self.assertAlmostEqual(calculated, expected, 8, "at index {0:d}\n"
                                                                "negative average expected:   {1:f}\n"
                                                                "negative average calculated: {2:f}".format(i,
                                                                                                            expected,
                                                                                                            calculated))

    def testMovingNegativeDifferenceAverageDeepcopy(self):
        mv = MovingNegativeDifferenceAverage(3, 'x')
        mv.push(dict(x=1.))
        mv.push(dict(x=-1.))
        mv.push(dict(x=2.))

        copied = copy.deepcopy(mv)
        self.assertAlmostEqual(mv.value, copied.value)

        data = np.random.randn(20)
        for d in data:
            mv.push(dict(x=d))
            copied.push(dict(x=d))

            self.assertAlmostEqual(mv.value, copied.value)

    def testMovingNegativeDifferenceAveragePickle(self):
        mv = MovingNegativeDifferenceAverage(3, 'x')
        mv.push(dict(x=1.))
        mv.push(dict(x=-1.))
        mv.push(dict(x=2.))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(mv, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)

        self.assertAlmostEqual(mv.value, pickled.value)

        data = np.random.randn(20)

        for d in data:
            mv.push(dict(x=d))
            pickled.push(dict(x=d))

            self.assertAlmostEqual(mv.value, pickled.value)

    def testMovingRSI(self):
        window = 10
        rsi = MovingRSI(window, 'x')
        pos_avg = MovingPositiveDifferenceAverage(window, 'x')
        neg_avg = MovingNegativeDifferenceAverage(window, 'x')
        for i, value in enumerate(self.sample):
            rsi.push(dict(x=value))
            pos_avg.push(dict(x=value))
            neg_avg.push(dict(x=value))

            calculated = rsi.value
            expected = pos_avg.value / (pos_avg.value - neg_avg.value) * 100
            if i > 0:
                self.assertAlmostEqual(calculated, expected, 8, "at index {0:d}\n"
                                                                "negative average expected:   {1:f}\n"
                                                                "negative average calculated: {2:f}".format(i,
                                                                                                            expected,
                                                                                                            calculated))

    def testMovingRSIDeepcopy(self):
        mv = MovingRSI(3, 'x')
        mv.push(dict(x=1.))
        mv.push(dict(x=-1.))
        mv.push(dict(x=2.))

        copied = copy.deepcopy(mv)
        self.assertAlmostEqual(mv.value, copied.value)

    def testMovingRSIPickle(self):
        mv = MovingRSI(3, 'x')
        mv.push(dict(x=1.))
        mv.push(dict(x=-1.))
        mv.push(dict(x=2.))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(mv, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)

        self.assertAlmostEqual(mv.value, pickled.value)

    def testMovingNegativeAverager(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/averagepostiveandnegative_random.csv')

        window = 20
        mv = MovingNegativeAverage(window, 'z')
        self.assertAlmostEqual(mv.result(), 0.0, 15)

        with open(filePath, 'r') as fileHandler:
            reader = csv.reader(fileHandler)

            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mv.push(dict(z=float(row[1])))
                if i >= window:
                    expected = float(row[7])
                    calculated = mv.result()
                    self.assertAlmostEqual(calculated, expected, 8, "at index {0:d}\n"
                                                                    "Positive average expected:   {1:f}\n"
                                                                    "positive average calculated: {2:f}".format(i,
                                                                                                                expected,
                                                                                                                calculated))

    def testMovingNegativeAverageDeepcopy(self):
        mv = MovingNegativeAverage(3, 'x')
        mv.push(dict(x=1.))
        mv.push(dict(x=-1.))
        mv.push(dict(x=2.))

        copied = copy.deepcopy(mv)
        self.assertAlmostEqual(mv.value, copied.value)

    def testMovingNegativeAveragePickle(self):
        mv = MovingNegativeAverage(3, 'x')
        mv.push(dict(x=1.))
        mv.push(dict(x=-1.))
        mv.push(dict(x=2.))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(mv, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)

        self.assertAlmostEqual(mv.value, pickled.value)

    def testMovingSum(self):
        window = 120
        total = 2500

        mv = MovingSum(window, 'z')
        runningSum = 0.0
        con = []
        for i in range(total):
            value = float(i)
            con.append(value)
            mv.push(dict(z=value))
            runningSum += value

            if i >= window:
                runningSum -= con[0]
                con = con[1:]

            if i >= window - 1:
                expected = runningSum
                calculated = mv.result()
                self.assertAlmostEqual(calculated, expected, 15, "at index {0:d}\n"
                                                                 "Sum expected:   {1:f}\n"
                                                                 "Sum calculated: {2:f}".format(i, expected,
                                                                                                calculated))

    def testMovingSumDeepcopy(self):
        ms = MovingSum(3, 'x')

        ms.push(dict(x=1.))
        ms.push(dict(x=2.))
        ms.push(dict(x=3.))

        copied = copy.deepcopy(ms)
        self.assertAlmostEqual(copied.value, ms.value)

    def testMovingSumPickle(self):
        ms = MovingSum(3, 'x')

        ms.push(dict(x=1.))
        ms.push(dict(x=2.))
        ms.push(dict(x=3.))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(ms, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(ms.value, pickled.value)
        os.unlink(f.name)

    def testMovingMax(self):
        window = 120

        mv = MovingMax(window, 'z')
        total = np.random.randn(2500)
        con = deque(maxlen=window)
        for i, value in enumerate(total):
            value = float(value)
            con.append(value)
            mv.push(dict(z=value))
            runningMax = max(con)

            expected = runningMax
            calculated = mv.result()
            self.assertAlmostEqual(calculated, expected, 15, "at index {0:d}\n"
                                                             "Max expected:   {1:f}\n"
                                                             "Max calculated: {2:f}".format(i, expected, calculated))

    def testMovingArgMax(self):
        window = 120

        mv = MovingArgMax(window, 'z')
        total = np.random.randn(2500)
        con = deque(maxlen=window)
        for i, value in enumerate(total):
            value = float(value)
            con.append(value)
            mv.push(dict(z=value))
            runningMax = max(con)

            expected = len(con) - np.where(np.array(con) == runningMax)[0][0] - 1.
            calculated = mv.result()
            self.assertAlmostEqual(calculated, expected, 15, "at index {0:d}\n"
                                                             "Max expected at:   {1:f}\n"
                                                             "Max calculated at: {2:f}".format(i, expected, calculated))

    def testMovingArgMin(self):
        window = 120

        mv = MovingArgMin(window, 'z')
        total = np.random.randn(2500)
        con = deque(maxlen=window)
        for i, value in enumerate(total):
            value = float(value)
            con.append(value)
            mv.push(dict(z=value))
            runningMin = min(con)

            expected = len(con) - np.where(np.array(con) == runningMin)[0][0] - 1.
            calculated = mv.result()
            self.assertAlmostEqual(calculated, expected, 15, "at index {0:d}\n"
                                                             "Min expected at:   {1:f}\n"
                                                             "Min calculated at: {2:f}".format(i, expected, calculated))

    def testMovingMaxDeepcopy(self):
        test = MovingMax(3, 'close')

        test.push(dict(close=3.0))
        test.push(dict(close=4.0))
        test.push(dict(close=2.0))

        copied = copy.deepcopy(test)
        self.assertAlmostEqual(copied.value, test.value)

    def testMovingMaxPickle(self):
        test = MovingMax(3, 'close')

        test.push(dict(close=3.0))
        test.push(dict(close=4.0))
        test.push(dict(close=2.0))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

    def testMovingMinimum(self):
        window = 120

        mv = MovingMin(window, 'z')
        total = np.random.randn(2500)
        con = deque(maxlen=window)
        for i, value in enumerate(total):
            value = float(value)
            con.append(value)
            mv.push(dict(z=value))
            runningMin = min(con)

            expected = runningMin
            calculated = mv.result()
            self.assertAlmostEqual(calculated, expected, 15, "at index {0:d}\n"
                                                             "Min expected:   {1:f}\n"
                                                             "Min calculated: {2:f}".format(i, expected, calculated))

    def testMovingMinimumDeepcopy(self):
        test = MovingMin(3, 'close')

        test.push(dict(close=3.0))
        test.push(dict(close=4.0))
        test.push(dict(close=2.0))

        copied = copy.deepcopy(test)
        self.assertAlmostEqual(copied.value, test.value)

    def testMovingMinimumPickle(self):
        test = MovingMin(3, 'close')

        test.push(dict(close=3.0))
        test.push(dict(close=4.0))
        test.push(dict(close=2.0))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

    def testMovingRank(self):
        window = 10

        mq = MovingRank(window, 'z')
        total = np.random.randn(2500)
        con = deque(maxlen=window)
        for i, value in enumerate(total):
            value = float(value)
            con.append(value)
            mq.push(dict(z=value))

            if i >= 1:
                calculated = mq.result()
                sorted_con = sorted(con)
                expected = sorted_con.index(value)
                self.assertAlmostEqual(calculated, expected, 15, "at index {0:d}\n"
                                                                 "Rank expected:   {1:f}\n"
                                                                 "Rank calculated: {2:f}".format(i,
                                                                                                 expected,
                                                                                                 calculated))

    def testMovingQuantile(self):
        window = 10

        mq = MovingQuantile(window, 'z')
        total = np.random.randn(2500)
        con = deque(maxlen=window)
        for i, value in enumerate(total):
            value = float(value)
            con.append(value)
            mq.push(dict(z=value))

            if i >= 1:
                calculated = mq.result()
                sorted_con = sorted(con)
                expected = sorted_con.index(value) / (len(sorted_con) - 1.)
                self.assertAlmostEqual(calculated, expected, 15, "at index {0:d}\n"
                                                                 "Quantile expected:   {1:f}\n"
                                                                 "Quantile calculated: {2:f}".format(i, expected,
                                                                                                     calculated))

    def testMovingQuantileDeepcopy(self):
        test = MovingQuantile(10, 'close')

        test.push(dict(close=3.0))
        test.push(dict(close=4.0))
        test.push(dict(close=2.0))
        test.push(dict(close=3.5))

        copied = copy.deepcopy(test)
        self.assertAlmostEqual(copied.value, test.value)

    def testMovingQuantilePickle(self):
        test = MovingQuantile(10, 'close')

        test.push(dict(close=3.0))
        test.push(dict(close=4.0))
        test.push(dict(close=2.0))
        test.push(dict(close=3.5))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

    def testMovingAllTrue(self):
        window = 3

        underlying = Latest('x') > 0.

        mat = MovingAllTrue(window, underlying)

        total = np.random.randn(2500)
        con = deque(maxlen=window)
        for i, value in enumerate(total):
            value = float(value)
            con.append(value)
            mat.push(dict(x=value))

            calculated = mat.result()
            expected = np.all(np.array(con) > 0.)

            self.assertEqual(calculated, expected, "at index {0}\n"
                                                   "Quantile expected:   {1}\n"
                                                   "Quantile calculated: {2}".format(i, expected, calculated))

    def testMovingAllTrueDeepcopy(self):
        test = MovingAllTrue(3, Latest('x') > 0.)

        test.push(dict(x=-3.0))
        test.push(dict(x=4.0))
        test.push(dict(x=2.0))
        test.push(dict(x=3.5))

        copied = copy.deepcopy(test)
        self.assertAlmostEqual(copied.value, test.value)

    def testMovingAllTruePickle(self):
        test = MovingAllTrue(3, Latest('x') > 0.)

        test.push(dict(x=3.0))
        test.push(dict(x=4.0))
        test.push(dict(x=2.0))
        test.push(dict(x=-3.5))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

    def testMovingAnyTrue(self):
        window = 3

        underlying = Latest('x') > 0.

        mat = MovingAnyTrue(window, underlying)

        total = np.random.randn(2500)
        con = deque(maxlen=window)
        for i, value in enumerate(total):
            value = float(value)
            con.append(value)
            mat.push(dict(x=value))

            calculated = mat.result()
            expected = np.any(np.array(con) > 0.)

            self.assertEqual(calculated, expected, "at index {0}\n"
                                                   "Quantile expected:   {1}\n"
                                                   "Quantile calculated: {2}".format(i, expected, calculated))

    def testMovingAnyTrueDeepcopy(self):
        test = MovingAnyTrue(3, Latest('x') > 0.)

        test.push(dict(x=-3.0))
        test.push(dict(x=-4.0))
        test.push(dict(x=2.0))
        test.push(dict(x=-3.5))

        copied = copy.deepcopy(test)
        self.assertAlmostEqual(copied.value, test.value)

    def testMovingAnyTruePickle(self):
        test = MovingAnyTrue(3, Latest('x') > 0.)

        test.push(dict(x=3.0))
        test.push(dict(x=-4.0))
        test.push(dict(x=-2.0))
        test.push(dict(x=-3.5))

        f = tempfile.NamedTemporaryFile('w+b', delete=False)
        pickle.dump(test, f)
        f.close()
        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

    def testMovingCountedPositive(self):
        window = 120
        total = 2500

        values = [1.0 if i % 2 else -1.0 for i in range(total)]
        mv = MovingCountedPositive(window, 'z')
        runningCount = 0
        con = []
        for i, value in enumerate(values):
            if i % 2:
                runningCount += 1
            con.append(i)
            mv.push(dict(z=value))

            if i >= window:
                if con[0] % 2:
                    runningCount -= 1
                con = con[1:]

            if i >= window - 1:
                expected = runningCount
                calculated = mv.result()
                self.assertAlmostEqual(calculated, expected, 15, "at index {0:d}\n"
                                                                 "Counted positive expected:   {1:f}\n"
                                                                 "Counted positive calculated: {2:f}".format(i,
                                                                                                             expected,
                                                                                                             calculated))

    def testMovingCountedPositiveDeepcopy(self):
        test = MovingCountedPositive(3, 'x')

        test.push(dict(x=-3.0))
        test.push(dict(x=-4.0))
        test.push(dict(x=2.0))
        test.push(dict(x=-3.5))

        copied = copy.deepcopy(test)
        self.assertAlmostEqual(copied.value, test.value)

    def testMovingCountedPositivePickle(self):
        test = MovingCountedPositive(3, 'x')

        test.push(dict(x=3.0))
        test.push(dict(x=-4.0))
        test.push(dict(x=-2.0))
        test.push(dict(x=-3.5))

        f = tempfile.NamedTemporaryFile('w+b', delete=False)
        pickle.dump(test, f)
        f.close()
        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

    def testMovingCountedNegative(self):
        window = 120
        total = 2500

        values = [1.0 if i % 2 else -1.0 for i in range(total)]
        mv = MovingCountedNegative(window, 'z')
        runningCount = 0
        con = []
        for i, value in enumerate(values):
            if not i % 2:
                runningCount += 1
            con.append(i)
            mv.push(dict(z=value))

            if i >= window:
                if not con[0] % 2:
                    runningCount -= 1
                con = con[1:]

            if i >= window - 1:
                expected = runningCount
                calculated = mv.result()
                self.assertAlmostEqual(calculated, expected, 15, "at index {0:d}\n"
                                                                 "Counted negative expected:   {1:f}\n"
                                                                 "Counted negative calculated: {2:f}".format(i,
                                                                                                             expected,
                                                                                                             calculated))

    def testMovingCountedNegativeDeepcopy(self):
        test = MovingCountedNegative(3, 'x')

        test.push(dict(x=-3.0))
        test.push(dict(x=-4.0))
        test.push(dict(x=2.0))
        test.push(dict(x=-3.5))

        copied = copy.deepcopy(test)
        self.assertAlmostEqual(copied.value, test.value)

    def testMovingCountedNegativePickle(self):
        test = MovingCountedNegative(3, 'x')

        test.push(dict(x=3.0))
        test.push(dict(x=-4.0))
        test.push(dict(x=-2.0))
        test.push(dict(x=-3.5))

        f = tempfile.NamedTemporaryFile('w+b', delete=False)
        pickle.dump(test, f)
        f.close()
        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

    def testMovingVariancer(self):
        window = 120
        total = 2500

        # Test moving population variance
        mv = MovingVariance(window, 'z', isPopulation=True)
        runningSum = 0.0
        runningSumSquare = 0.0
        con = []
        for i in range(total):
            value = float(i)
            con.append(value)
            mv.push(dict(z=value))
            runningSum += value
            runningSumSquare += value * value

            if i >= window:
                runningSum -= con[0]
                runningSumSquare -= con[0] * con[0]
                con = con[1:]

            if i >= window - 1:
                expected = (runningSumSquare - runningSum * runningSum / window) / window
                calculated = mv.result()
                self.assertAlmostEqual(calculated, expected, 15, "at index {0:d}\n"
                                                                 "Var expected:   {1:f}\n"
                                                                 "Var calculated: {2:f}".format(i, expected,
                                                                                                calculated))

        # Test moving sample variance
        mv = MovingVariance(window, 'z', isPopulation=False)
        runningSum = 0.0
        runningSumSquare = 0.0
        con = []
        for i in range(total):
            value = float(i)
            con.append(value)
            mv.push(dict(z=value))
            runningSum += value
            runningSumSquare += value * value

            if i == 0:
                self.assertTrue(np.isnan(mv.result()))

            if i >= window:
                runningSum -= con[0]
                runningSumSquare -= con[0] * con[0]
                con = con[1:]

            length = window if i >= window else (i + 1)
            if i >= window - 1:
                expected = (runningSumSquare - runningSum * runningSum / length) / (length - 1)
                calculated = mv.result()
                self.assertAlmostEqual(calculated, expected, 15, "at index {0:d}\n"
                                                                 "Var expected:   {1:f}\n"
                                                                 "Var calculated: {2:f}".format(i, expected,
                                                                                                calculated))

    def testMovingVarianceDeepcopy(self):
        window = 20
        mv = MovingVariance(window, 'x')

        mv.push(dict(x=1.))
        mv.push(dict(x=2.))

        copied = copy.deepcopy(mv)
        self.assertAlmostEqual(copied.value, mv.value)

        for i in range(3, 40):
            mv.push(dict(x=float(i)))

        copied = copy.deepcopy(mv)
        self.assertAlmostEqual(copied.value, mv.value)

    def testMovingVariancePickle(self):
        window = 20
        mv = MovingVariance(window, 'x')

        mv.push(dict(x=1.))
        mv.push(dict(x=2.))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(mv, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(mv.value, pickled.value)
        os.unlink(f.name)

        for i in range(3, 40):
            mv.push(dict(x=float(i)))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(mv, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(mv.value, pickled.value)
        os.unlink(f.name)

    def testMovingStandardDeviation(self):
        window = 120
        total = 2500

        # Test moving population variance
        mv = MovingStandardDeviation(window, 'z', isPopulation=True)
        runningSum = 0.0
        runningSumSquare = 0.0
        con = []
        for i in range(total):
            value = float(i)
            con.append(value)
            mv.push(dict(z=value))
            runningSum += value
            runningSumSquare += value * value

            if i >= window:
                runningSum -= con[0]
                runningSumSquare -= con[0] * con[0]
                con = con[1:]

            if i >= window - 1:
                expected = math.sqrt((runningSumSquare - runningSum * runningSum / window) / window)
                calculated = mv.result()
                self.assertAlmostEqual(calculated, expected, 15, "at index {0:d}\n"
                                                                 "Var expected:   {1:f}\n"
                                                                 "Var calculated: {2:f}".format(i, expected,
                                                                                                calculated))

        # Test moving sample variance
        mv = MovingVariance(window, 'z', isPopulation=False)
        runningSum = 0.0
        runningSumSquare = 0.0
        con = []
        for i in range(total):
            value = float(i)
            con.append(value)
            mv.push(dict(z=value))
            runningSum += value
            runningSumSquare += value * value

            if i == 0:
                self.assertTrue(np.isnan(mv.result()))

            if i >= window:
                runningSum -= con[0]
                runningSumSquare -= con[0] * con[0]
                con = con[1:]

            length = window if i >= window else (i + 1)
            if i >= window - 1:
                expected = (runningSumSquare - runningSum * runningSum / length) / (length - 1)
                calculated = mv.result()
                self.assertAlmostEqual(calculated, expected, 15, "at index {0:d}\n"
                                                                 "Var expected:   {1:f}\n"
                                                                 "Var calculated: {2:f}".format(i, expected,
                                                                                                calculated))

    def testMovingStandardDeviationDeepcopy(self):
        window = 20
        mv = MovingStandardDeviation(window, 'x')

        mv.push(dict(x=1.))
        mv.push(dict(x=2.))

        copied = copy.deepcopy(mv)
        self.assertAlmostEqual(copied.value, mv.value)

        for i in range(3, 40):
            mv.push(dict(x=float(i)))

        copied = copy.deepcopy(mv)
        self.assertAlmostEqual(copied.value, mv.value)

    def testMovingStandardDeviationPickle(self):
        window = 20
        mv = MovingStandardDeviation(window, 'x')

        mv.push(dict(x=1.))
        mv.push(dict(x=2.))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(mv, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(mv.value, pickled.value)
        os.unlink(f.name)

        for i in range(3, 40):
            mv.push(dict(x=float(i)))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(mv, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(mv.value, pickled.value)
        os.unlink(f.name)

    def testMovingNegativeVariancer(self):
        # test without enough negative value
        mv = MovingNegativeVariance(20, 'z', isPopulation=True)
        mv.push(dict(z=20.))

        self.assertTrue(np.isnan(mv.result()))

        mv = MovingNegativeVariance(20, 'z', isPopulation=False)
        mv.push(dict(z=20.))
        mv.push(dict(z=-20.))

        self.assertTrue(np.isnan(mv.result()))

        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/negativevariance.csv')

        window = 20
        mv = MovingNegativeVariance(window, 'z')

        with open(filePath, 'r') as fileHandler:
            reader = csv.reader(fileHandler)
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mv.push(dict(z=float(row[1])))

                if mv._runningNegativeCount == 1:
                    self.assertTrue(np.isnan(mv.result()))

                if i >= window:
                    expected = float(row[6])
                    calculated = mv.result()
                    self.assertAlmostEqual(calculated, expected, 7, "at index {0:d}\n"
                                                                    "Negative variance expected:   {1:f}\n"
                                                                    "Negative variance calculated: {2:f}".format(i,
                                                                                                                 expected,
                                                                                                                 calculated))

    def testMovingNegativeVarianceDeepcopy(self):
        window = 20
        mv = MovingNegativeVariance(window, 'x')

        mv.push(dict(x=-1.))
        mv.push(dict(x=-2.))

        copied = copy.deepcopy(mv)
        self.assertAlmostEqual(copied.value, mv.value)

        datas = np.random.randn(40)
        for i in datas:
            mv.push(dict(x=i))

        copied = copy.deepcopy(mv)
        self.assertAlmostEqual(copied.value, mv.value)

    def testMovingNegativeVariancePickle(self):
        window = 20
        mv = MovingNegativeVariance(window, 'x')

        mv.push(dict(x=-1.))
        mv.push(dict(x=-2.))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(mv, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(mv.value, pickled.value)
        os.unlink(f.name)

        datas = np.random.randn(40)
        for i in datas:
            mv.push(dict(x=i))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(mv, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(mv.value, pickled.value)
        os.unlink(f.name)

    def testMovingCorrelation(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/correlation.csv')

        window = 120
        mv = MovingCorrelation(window, 'z', 't')

        with open(filePath, 'r') as fileHandler:
            reader = csv.reader(fileHandler)

            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mv.push(dict(z=float(row[0]), t=float(row[1])))

                if i == 1:
                    self.assertTrue(np.isnan(mv.result()))

                if i >= window:
                    expected = float(row[2])
                    calculated = mv.result()
                    self.assertAlmostEqual(calculated, expected, 8, "at index {0:d}\n"
                                                                    "Correlation expected:   {1:f}\n"
                                                                    "Correlation calculated: {2:f}".format(i, expected,
                                                                                                           calculated))

    def testMovingProduct(self):
        window = 10
        mp = MovingProduct(window, 'x')

        con = []
        for i, value in enumerate(self.sample):
            con.append(value)
            mp.push(dict(x=value))
            if i >= window:
                con = con[1:]
            if i >= window - 1:
                expected = np.product(con)
                calculated = mp.result()
                self.assertAlmostEqual(expected, calculated, 8, "at index {0:d}\n"
                                                                "product expected:   {1:f}\n"
                                                                "product calculated: {2:f}".format(i, expected,
                                                                                                   calculated))

    def testMovingProductDeepcopy(self):
        window = 10
        mv = MovingProduct(window, 'x')

        mv.push(dict(x=1.))
        mv.push(dict(x=2.))

        copied = copy.deepcopy(mv)
        self.assertAlmostEqual(copied.value, mv.value)

        for i in range(3, 20):
            mv.push(dict(x=float(i)))

        copied = copy.deepcopy(mv)
        self.assertAlmostEqual(copied.value, mv.value)

    def testMovingProductPickle(self):
        window = 10
        mv = MovingProduct(window, 'x')

        mv.push(dict(x=1.))
        mv.push(dict(x=2.))

        f = tempfile.NamedTemporaryFile('w+b', delete=False)
        pickle.dump(mv, f)
        f.close()
        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(mv.value, pickled.value)
        os.unlink(f.name)

        for i in range(3, 20):
            mv.push(dict(x=float(i)))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(mv, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(mv.value, pickled.value)
        os.unlink(f.name)

    def testMACD(self):
        macd = MACD(5, 10, 'close')
        short_average = XAverage(5, 'close')
        long_average = XAverage(10, 'close')

        for i, value in enumerate(self.sample):
            macd.push(dict(close=value))
            short_average.push(dict(close=value))
            long_average.push(dict(close=value))
            expected = short_average.result() - long_average.result()

            calculated = macd.result()
            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected x-average:   {1:f}\n"
                                                             "calculated x-average: {2:f}".format(i,
                                                                                                  expected,
                                                                                                  calculated))

    def tesMACDDeepcopy(self):
        mv = MACD(5, 10, 'x')

        mv.push(dict(x=-1.))
        mv.push(dict(x=-2.))

        copied = copy.deepcopy(mv)
        self.assertAlmostEqual(copied.value, mv.value)

        datas = np.random.randn(40)
        for i in datas:
            mv.push(dict(x=i))

        copied = copy.deepcopy(mv)
        self.assertAlmostEqual(copied.value, mv.value)

    def testMACDPickle(self):
        mv = MACD(5, 10, 'x')

        mv.push(dict(x=-1.))
        mv.push(dict(x=-2.))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(mv, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(mv.value, pickled.value)
        os.unlink(f.name)

        datas = np.random.randn(40)
        for i in datas:
            mv.push(dict(x=i))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(mv, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(mv.value, pickled.value)
        os.unlink(f.name)

    def testEMAMACD(self):
        fast = 5
        slow = 10
        ema_window = 10
        macd = MACD(fast, slow, 'close')
        ema_macd = XAverage(ema_window, macd)

        macd_diff = macd - ema_macd

        for i, value in enumerate(self.sample):
            macd.push(dict(close=value))
            ema_macd.push(dict(close=value))
            macd_diff.push(dict(close=value))
            expected = macd.value - ema_macd.value
            calculated = macd_diff.value
            self.assertAlmostEqual(expected, calculated, 10, "at index {0:d}\n"
                                                             "expected ema macd diff:   {1:f}\n"
                                                             "calculated ema macd diff: {2:f}".format(i, expected,
                                                                                                      calculated))

    def testMovingResidue(self):
        window = 100
        x_data = np.random.randn(10000)

        mr = MovingResidue(window, x='x', y='y')

        for i, value in enumerate(zip(x_data, self.sample)):
            x = value[0]
            y = value[1]

            mr.push(dict(x=x, y=y))

            if i >= window - 1:
                series_x = x_data[i - window + 1:i + 1]
                series_y = self.sample[i - window + 1:i + 1]

                calculated_res = mr.result()
                expected_res = y - np.dot(series_x, series_y) / np.dot(series_x, series_x) * x
                self.assertAlmostEqual(expected_res, calculated_res, 8, "at index of {0:d}\n"
                                                                        "expected res:  {1:f}\n"
                                                                        "calculated res:{2:f}".format(i,
                                                                                                      expected_res,
                                                                                                      calculated_res))

    def testMovingResidueDeepcopy(self):
        window = 10
        mr = MovingResidue(window, x='x', y='y')

        mr.push(dict(x=-1., y=0))
        mr.push(dict(x=-2., y=-1))
        mr.push(dict(x=-3., y=-2))
        mr.push(dict(x=-4., y=-3))

        copied = copy.deepcopy(mr)

        datas = np.random.randn(40)
        for i in datas:
            mr.push(dict(x=i, y=i + 1.))
            copied.push(dict(x=i, y=i + 1))

        self.assertAlmostEqual(copied.value, mr.value)

    def testMovingResiduePickle(self):
        window = 10
        mr = MovingResidue(window, x='x', y='y')

        mr.push(dict(x=-1., y=0))
        mr.push(dict(x=-2., y=-1))
        mr.push(dict(x=-3., y=-2))

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(mr, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)

        datas = np.random.randn(40)
        for i in datas:
            mr.push(dict(x=i, y=i + 1.))
            pickled.push(dict(x=i, y=i + 1.))

        self.assertAlmostEqual(mr.value, pickled.value)
        os.unlink(f.name)

    def testShiftStr(self):
        s = Shift(2, Latest('roe'))
        self.assertEqual("\mathrm{Shift}(''\\text{roe}'', 2)", str(s))

    def testMovingMaxStr(self):
        s = MovingMax(10, 'roe')
        self.assertEqual("\mathrm{MMax}(10, ''\\text{roe}'')", str(s))

        s = MovingMax(10, Latest('roe') + Latest('y'))
        self.assertEqual("\mathrm{MMax}(10, ''\\text{roe}'' + ''\\text{y}'')", str(s))

    def testMovingMinStr(self):
        s = MovingMin(10, 'roe')
        self.assertEqual("\mathrm{MMin}(10, ''\\text{roe}'')", str(s))

        s = MovingMin(10, Latest('roe') + Latest('y'))
        self.assertEqual("\mathrm{MMin}(10, ''\\text{roe}'' + ''\\text{y}'')", str(s))

    def testMovingQuantileStr(self):
        s = MovingQuantile(10, 'roe')
        self.assertEqual("\mathrm{MQuantile}(10, ''\\text{roe}'')", str(s))

        s = MovingQuantile(10, Latest('roe') + Latest('y'))
        self.assertEqual("\mathrm{MQuantile}(10, ''\\text{roe}'' + ''\\text{y}'')", str(s))

    def testMovingAllTrueStr(self):
        s = MovingAllTrue(10, 'roe')
        self.assertEqual("\mathrm{MAllTrue}(10, ''\\text{roe}'')", str(s))

        s = MovingAllTrue(10, Latest('roe') + Latest('y'))
        self.assertEqual("\mathrm{MAllTrue}(10, ''\\text{roe}'' + ''\\text{y}'')", str(s))

    def testMovingAnyTrueStr(self):
        s = MovingAnyTrue(10, 'roe')
        self.assertEqual("\mathrm{MAnyTrue}(10, ''\\text{roe}'')", str(s))

        s = MovingAnyTrue(10, Latest('roe') + Latest('y'))
        self.assertEqual("\mathrm{MAnyTrue}(10, ''\\text{roe}'' + ''\\text{y}'')", str(s))

    def testMovingSumStr(self):
        s = MovingSum(10, 'roe')
        self.assertEqual("\mathrm{MSum}(10, ''\\text{roe}'')", str(s))

        s = MovingSum(10, Latest('roe') + Latest('y'))
        self.assertEqual("\mathrm{MSum}(10, ''\\text{roe}'' + ''\\text{y}'')", str(s))

    def testMovingResidueResStr(self):
        s = MovingResidue(10, x='roe', y='y')
        self.assertEqual("\mathrm{Res}(10, ''\\text{roe}'', ''\\text{y}'')", str(s))

        s = MovingResidue(10, x=Latest('roe'), y=Latest('y'))
        self.assertEqual("\mathrm{Res}(10, ''\\text{roe}'', ''\\text{y}'')", str(s))


if __name__ == '__main__':
    unittest.main()
