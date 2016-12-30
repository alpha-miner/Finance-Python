# -*- coding: utf-8 -*-
u"""
Created on 2015-7-16

@author: cheng.li
"""

import unittest
import csv
import os
import numpy as np
from collections import deque
from PyFin.Math.Accumulators import Shift
from PyFin.Math.Accumulators import MovingMax
from PyFin.Math.Accumulators import MovingMinimum
from PyFin.Math.Accumulators import MovingAverage
from PyFin.Math.Accumulators import MovingPositiveAverage
from PyFin.Math.Accumulators import MovingNegativeAverage
from PyFin.Math.Accumulators import MovingPositiveDifferenceAverage
from PyFin.Math.Accumulators import MovingNegativeDifferenceAverage
from PyFin.Math.Accumulators import MovingRSI
from PyFin.Math.Accumulators import MovingSum
from PyFin.Math.Accumulators import MovingCountedPositive
from PyFin.Math.Accumulators import MovingCountedNegative
from PyFin.Math.Accumulators import MovingVariance
from PyFin.Math.Accumulators import MovingNegativeVariance
from PyFin.Math.Accumulators import MovingHistoricalWindow
from PyFin.Math.Accumulators import MovingCorrelation
from PyFin.Math.Accumulators import MovingCorrelationMatrix
from PyFin.Math.Accumulators import MovingProduct
from PyFin.Math.Accumulators import MovingCenterMoment
from PyFin.Math.Accumulators import MovingSkewness
from PyFin.Math.Accumulators import MovingMaxPos
from PyFin.Math.Accumulators import MovingMinPos
from PyFin.Math.Accumulators import MovingKurtosis
from PyFin.Math.Accumulators import MovingRSV
from PyFin.Math.Accumulators import MACD
from PyFin.Math.Accumulators import XAverage
from PyFin.Math.Accumulators import MovingRank
from PyFin.Math.Accumulators import MovingKDJ
from PyFin.Math.Accumulators import MovingBias
from PyFin.Math.Accumulators import MovingAroon
from PyFin.Math.Accumulators import MovingLevel
from PyFin.Math.Accumulators import MovingAutoCorrelation

class TestStatefulAccumulators(unittest.TestCase):
    def setUp(self):
        np.random.seed(0)
        self.sample = np.random.randn(10000)

    def testShiftValueHolder(self):
        ma = MovingAverage(10, 'close')

        with self.assertRaises(ValueError):
            _ = Shift(ma, N=0)

        test = Shift(ma, N=1)

        test.push(dict(close=2.0))
        ma.push(dict(close=2.0))
        previous = ma.result()
        test.push(dict(close=5.0))
        ma.push(dict(close=5.0))

        self.assertAlmostEqual(previous, test.result())

        previous = ma.result()
        test.push(dict(close=10.0))
        self.assertAlmostEqual(previous, test.result())

    def testMovingAverager(self):
        window = 120
        total = 2500

        mv = MovingAverage(window, dependency='z')
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

    def testMovingPositiveAverager(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/averagepostiveandnegative_random.csv')

        window = 20
        mv = MovingPositiveAverage(window, dependency='z')
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

    def testMovingPositiveDifferenceAverage(self):
        window = 10
        mv = MovingPositiveDifferenceAverage(window=window, dependency='x')

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

    def testMovingNegativeDifferenceAverage(self):
        window = 10
        mv = MovingNegativeDifferenceAverage(window=window, dependency='x')

        last = self.sample[0]
        diff_list = []
        for i, value in enumerate(self.sample):
            mv.push(dict(x=value))
            diff = value - last
            if i > 0:
                diff_list.append(diff)
            last = value
            neg_list = np.minimum(diff_list[-window:], 0.)

            expected = 0. if np.isnan(np.mean(neg_list)) else np.mean(neg_list)
            calculated = mv.result()
            if i > 0:
                self.assertAlmostEqual(calculated, expected, 8, "at index {0:d}\n"
                                                                "negative average expected:   {1:f}\n"
                                                                "negative average calculated: {2:f}".format(i,
                                                                                                            expected,
                                                                                                            calculated))

    def testMovingRSI(self):
        window = 10
        rsi = MovingRSI(window=window, dependency='x')
        pos_avg = MovingPositiveDifferenceAverage(window=window, dependency='x')
        neg_avg = MovingNegativeDifferenceAverage(window=window, dependency='x')
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

    def testMovingNegativeAverager(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/averagepostiveandnegative_random.csv')

        window = 20
        mv = MovingNegativeAverage(window, dependency='z')
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

    def testMovingSum(self):
        window = 120
        total = 2500

        mv = MovingSum(window, dependency=['z'])
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

    def testMovingMax(self):
        window = 120

        mv = MovingMax(window, dependency='z')
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

    def testMovingMinimum(self):
        window = 120

        mv = MovingMinimum(window, dependency='z')
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

    def testMovingCountedPositive(self):
        window = 120
        total = 2500

        values = [1.0 if i % 2 else -1.0 for i in range(total)]
        mv = MovingCountedPositive(window, dependency='z')
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

    def testMovingCountedNegative(self):
        window = 120
        total = 2500

        values = [1.0 if i % 2 else -1.0 for i in range(total)]
        mv = MovingCountedNegative(window, dependency='z')
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

    def testMovingVariancer(self):
        window = 120
        total = 2500

        # Test moving population variance
        mv = MovingVariance(window, dependency='z', isPopulation=True)
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
        mv = MovingVariance(window, dependency='z', isPopulation=False)
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

    def testMovingNegativeVariancer(self):
        # test without enough negative value
        mv = MovingNegativeVariance(20, dependency='z', isPopulation=True)
        mv.push(dict(z=20.))

        self.assertTrue(np.isnan(mv.result()))

        mv = MovingNegativeVariance(20, dependency='z', isPopulation=False)
        mv.push(dict(z=20.))
        mv.push(dict(z=-20.))

        self.assertTrue(np.isnan(mv.result()))

        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/negativevariance.csv')

        window = 20
        mv = MovingNegativeVariance(window, dependency='z')

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

    def testMovingHistoricalWindow(self):
        # test simple historical value holder
        window = 5
        mh = MovingHistoricalWindow(window, "x")
        benchmarkContainer = deque(maxlen=window)
        for i, data in enumerate(self.sample):
            mh.push(dict(x=data))
            benchmarkContainer.append(data)

            if i == 0:
                with self.assertRaises(ValueError):
                    _ = mh[1]

            for k in range(mh.size):
                expected = benchmarkContainer[mh.size - 1 - k]
                calculated = mh[k]
                self.assertAlmostEqual(expected, calculated)

        # test compounded historical value holder
        ma = MovingSum(window, 'x')
        mh = MovingHistoricalWindow(window, ma)
        benchmarkContainer = deque(maxlen=window)
        for i, data in enumerate(self.sample):
            ma.push(dict(x=data))
            mh.push(dict(x=data))
            benchmarkContainer.append(ma.value)

            if i == 0:
                with self.assertRaises(ValueError):
                    _ = mh[1]

            for k in range(mh.size):
                expected = benchmarkContainer[mh.size - 1 - k]
                calculated = mh[k]
                self.assertAlmostEqual(expected, calculated, 12, "at index {0} and position {1}\n"
                                                                 "expected:   {2}\n"
                                                                 "calculated: {3}".format(i, k, expected, calculated))

    def testMovingCorrelation(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/correlation.csv')

        window = 120
        mv = MovingCorrelation(window, dependency=['z', 't'])

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

    def testMovingCorrelationMatrix(self):

        first100Sample = [[1.00000000, -0.02300376, -0.05491407, -0.12810836, -0.16975843],
                          [-0.02300376, 1.00000000, -0.15040039, 0.07712015, 0.05539850],
                          [-0.05491407, -0.15040039, 1.00000000, -0.03660999, 0.20378756],
                          [-0.12810836, 0.07712015, -0.03660999, 1.00000000, 0.08112261],
                          [-0.16975843, 0.05539850, 0.20378756, 0.08112261, 1.00000000]]

        last100Sample = [[1.000000000, 0.105645822, -0.084754465, 0.033285925, -0.064632300],
                         [0.105645822, 1.000000000, -0.025033153, 0.094747896, 0.000483146],
                         [-0.084754465, -0.025033153, 1.000000000, -0.010053933, -0.131093043],
                         [0.033285925, 0.094747896, -0.010053933, 1.000000000, -0.043928037],
                         [-0.064632300, 0.000483146, -0.131093043, -0.043928037, 1.000000000]]

        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/correlationmatrix.csv')

        window = 100

        mv = MovingCorrelationMatrix(window, dependency='samples')

        with open(filePath, 'r') as fileHandler:
            reader = csv.reader(fileHandler)

            for i, row in enumerate(reader):
                row = [float(value) for value in row]
                mv.push(dict(samples=row))
                if i == 0:
                    self.assertTrue(np.all(np.isnan(mv.result())))
                if (i + 1) == window:
                    calculated = mv.result()
                    for k, row in enumerate(first100Sample):
                        for j, corr in enumerate(row):
                            self.assertAlmostEqual(calculated[k][j], corr, 8,
                                                   "First 100 sample correlation matrix different at ({0:d}, {1:d})\n"
                                                   "Expected: {2:f}\n"
                                                   "Calculated: {3:f}".format(k, j, corr, calculated[k][j]))
                if (i + 1) == 1000:
                    calculated = mv.result()
                    for k, row in enumerate(last100Sample):
                        for j, corr in enumerate(row):
                            self.assertAlmostEqual(calculated[k][j], corr, 8,
                                                   "Last 100 sample correlation matrix different at ({0:d}, {1:d})\n"
                                                   "Expected: {2:f}\n"
                                                   "Calculated: {3:f}".format(k, j, corr, calculated[k][j]))



    def testMovingProduct(self):
        window = 10
        mp = MovingProduct(window, dependency='x')

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


    def testMovingCenterMoment(self):
        window = 10
        order = 1
        mm = MovingCenterMoment(window, order, dependency='x')

        con = []
        for i, value in enumerate(self.sample):
            con.append(value)
            mm.push(dict(x=value))
            if i >= window:
                con = con[1:]
            if i >= window - 1:
                expected = np.mean(np.power(np.abs(np.array(con) - np.mean(con)), order))
                calculated = mm.result()
                self.assertAlmostEqual(expected, calculated, 8, "at index {0:d}\n"
                                                                "moment expected:   {1:f}\n"
                                                                "moment calculated: {2:f}".format(i, expected,
                                                                                                  calculated))


        window = 10
        order = 2
        mm = MovingCenterMoment(window, order, dependency='x')

        con = []
        for i, value in enumerate(self.sample):
            con.append(value)
            mm.push(dict(x=value))
            if i >= window:
                con = con[1:]
            if i >= window - 1:
                expected = np.mean(np.power(np.abs(np.array(con) - np.mean(con)), order))
                calculated = mm.result()
                self.assertAlmostEqual(expected, calculated, 8, "at index {0:d}\n"
                                                                "moment expected:   {1:f}\n"
                                                                "moment calculated: {2:f}".format(i, expected,
                                                                                                  calculated))


    def testMovingSkewness(self):
        window = 10
        ms = MovingSkewness(window, dependency='x')

        con = []
        for i, value in enumerate(self.sample):
            con.append(value)
            ms.push(dict(x=value))
            if i >= window:
                con = con[1:]
            if i >= window - 1:
                calculated = ms.result()
                this_moment3 = np.mean(np.power(np.abs(np.array(con) - np.mean(con)), 3))
                expected = this_moment3 / np.power(np.std(con), 3)
                self.assertAlmostEqual(expected, calculated, 8, "at index {0:d}\n"
                                                                "skewness expected:   {1:f}\n"
                                                                "skewness calculated: {2:f}".format(i, expected,
                                                                                                  calculated))


    def testMovingTsMaxPos(self):
        window = 10
        maxPos = MovingMaxPos(window, dependency='x')

        con = []
        for i, value in enumerate(self.sample):
            con.append(value)
            maxPos.push(dict(x=value))
            if i >= window:
                con = con[1:]
            if i >= window - 1:
                calculated = maxPos.result()
                expected = con.index(np.max(con))
                self.assertEqual(expected, calculated, "at index {0:d}\n"
                                                        "maxPos expected:   {1:f}\n"
                                                        "maxPos calculated: {2:f}".format(i, expected,
                                                                                              calculated))


    def testMovingTsMinPos(self):
        window = 10
        minPos = MovingMinPos(window, dependency='x')

        con = []
        for i, value in enumerate(self.sample):
            con.append(value)
            minPos.push(dict(x=value))
            if i >= window:
                con = con[1:]
            if i >= window - 1:
                calculated = minPos.result()
                expected = con.index(np.min(con))
                self.assertEqual(expected, calculated, "at index {0:d}\n"
                                                       "minPos expected:   {1:f}\n"
                                                       "minPos calculated: {2:f}".format(i, expected,
                                                                                         calculated))


    def testMovingKurtosis(self):
        window = 10
        mk = MovingKurtosis(window, dependency='x')

        con = []
        for i, value in enumerate(self.sample):
            con.append(value)
            mk.push(dict(x=value))
            if i >= window:
                con = con[1:]
            if i >= window - 1:
                calculated = mk.result()
                this_moment4 = np.mean(np.power(np.abs(np.array(con) - np.mean(con)), 4))
                expected = this_moment4 / np.power(np.std(con), 4)
                self.assertAlmostEqual(expected, calculated, 8, "at index {0:d}\n"
                                                                "kurtosis expected:   {1:f}\n"
                                                                "kurtosis calculated: {2:f}".format(i, expected,
                                                                                                    calculated))


    def testMovingRSV(self):
        window = 10
        rsv = MovingRSV(window, dependency='x')

        con = []
        for i, value in enumerate(self.sample):
            con.append(value)
            rsv.push(dict(x=value))
            if i >= window:
                con = con[1:]
            if i >= window - 1:
                calculated = rsv.result()
                expected = (value - np.min(con)) / (np.max(con) - np.min(con))
                self.assertAlmostEqual(expected, calculated, 8, "at index {0:d}\n"
                                                                "rsv expected:   {1:f}\n"
                                                                "rsv calculated: {2:f}".format(i, expected,
                                                                                               calculated))


    def testMACD(self):
        macd = MACD(short=5, long=10, dependency='close')
        short_average = XAverage(window=5, dependency='close')
        long_average = XAverage(window=10, dependency='close')

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
                                                             "calculated ema macd diff: {2:f}".format(i, expected, calculated))


    def testMovingRank(self):
        window = 10
        mk = MovingRank(window, dependency='x')

        con = []
        for i, value in enumerate(self.sample):
            con.append(value)
            mk.push(dict(x=value))
            if i >= window:
                con = con[1:]
            if i >= window - 1:
                calculated = mk.result()
                expected = np.argsort(np.argsort(con))
                self.assertListEqual(list(expected), calculated, "at index {0:d}\n"
                                                            "expected rank:   {1}\n"
                                                            "calculated rank: {2}".format(i, expected, calculated))

    def testMovingKDJ(self):
        window = 10
        k=3
        d=3
        mk = MovingKDJ(window, dependency='x')

        con = []
        this_j = []
        for i, value in enumerate(self.sample):
            con.append(value)
            mk.push(dict(x=value))
            if i >= window:
                con = con[1:]
            if len(con) == 1:
                this_j.append(np.nan)
            else:
                this_rsv = (value - np.min(con)) / (np.max(con) - np.min(con))
                if len(con) == 2:
                    this_k = (0.5 * (k - 1) + this_rsv) / k
                    this_d = (0.5 * (d - 1) + this_k) / d
                else:
                    this_k = (this_k * (k - 1) + this_rsv) / k
                    this_d = (this_d * (d - 1) + this_k) / d
                this_j.append(3 * this_k - 2 * this_d)

            if i >= window - 1:
                expected = this_j[-1]
                calculated = mk.result()
                self.assertAlmostEqual(expected, calculated, 8, "at index {0:d}\n"
                                                                "expected kdj:   {1:f}\n"
                                                                "calculated kdj: {2:f}".format(i, expected, calculated))



    def testMovingBias(self):
        window = 10
        mb = MovingBias(window, dependency='x')
        con = []

        for i, value in enumerate(self.sample):
            con.append(value)
            mb.push(dict(x=value))
            if i >= window:
                con = con[1:]
            if i >= window - 1:
                calculated = mb.result()
                expected = value / np.mean(con) - 1
                self.assertAlmostEqual(expected, calculated, 8, "at index {0:d}\n"
                                                                "expected bias:   {1:f}\n"
                                                                "calculated bias: {2:f}".format(i, expected, calculated))


    def testMovingAroon(self):
        window = 10
        ma = MovingAroon(window, dependency='x')
        con = []

        for i, value in enumerate(self.sample):
            con.append(value)
            ma.push(dict(x=value))
            if i >= window:
                con = con[1:]
            if i >= window - 1:
                calculated = ma.result()
                expected = (con.index(np.max(con)) - con.index(np.min(con))) / window
                self.assertAlmostEqual(expected, calculated, 8, "at index {0:d}\n"
                                                                "expected aroon:  {1:f}\n"
                                                                "calculated aroon:{2:f}".format(i, expected, calculated))

    def testMovingLevel(self):
        window = 10
        ml = MovingLevel(window, dependency='x')
        con = []

        for i, value in enumerate(self.sample):
            con.append(value)
            ml.push(dict(x=value))
            if i >= window:
                con = con[1:]
            if i >= window - 1:
                calculated = ml.result()
                expected = con[-1] / con[0]
                self.assertAlmostEqual(expected, calculated, 8, "at index {0:d}\n"
                                                                "expected level:   {1:f}\n"
                                                                "calculated level: {2:f}".format(i, expected, calculated))


    def testMovingAutoCorrelation(self):
        window = 10
        lags = 2
        ma = MovingAutoCorrelation(window, lags, dependency='x')
        con = []

        for i, value in enumerate(self.sample):
            con.append(value)
            ma.push(dict(x=value))
            if i >= window:
                con = con[1:]
            if i >= window - 1:
                calculated = ma.result()
                con_forward = con[0:window - lags]
                con_backward = con[-window + lags - 1 : -1]
                expected = np.cov(con_backward, con_forward) / (np.std(con_forward) * np.std(con_backward))
                self.assertAlmostEqual(expected[0, 1], calculated, 8, "at index of {0:d}\n"
                                                                        "expected autoCorr:  {1:f}\n"
                                                                        "calculated autoCorr:{2:f}".format(i, expected[0,1],
                                                                                                           calculated))

if __name__ == '__main__':
    unittest.main()
    
