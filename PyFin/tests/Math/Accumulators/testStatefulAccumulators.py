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
from PyFin.Math.Accumulators import MovingSum
from PyFin.Math.Accumulators import MovingCountedPositive
from PyFin.Math.Accumulators import MovingCountedNegative
from PyFin.Math.Accumulators import MovingVariance
from PyFin.Math.Accumulators import MovingNegativeVariance
from PyFin.Math.Accumulators import MovingHistoricalWindow
from PyFin.Math.Accumulators import MovingCorrelation
from PyFin.Math.Accumulators import MovingCorrelationMatrix


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
                with self.assertRaises(ArithmeticError):
                    mv.result()

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

        with self.assertRaises(ArithmeticError):
            _ = mv.result()

        mv = MovingNegativeVariance(20, dependency='z', isPopulation=False)
        mv.push(dict(z=20.))
        mv.push(dict(z=-20.))

        with self.assertRaises(ArithmeticError):
            _ = mv.result()

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
                    with self.assertRaises(ArithmeticError):
                        mv.result()

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
                    with self.assertRaises(ArithmeticError):
                        _ = mv.result()

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
                    with self.assertRaises(ArithmeticError):
                        _ = mv.result()
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
