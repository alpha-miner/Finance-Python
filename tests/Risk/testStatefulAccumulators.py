# -*- coding: utf-8 -*-
u"""
Created on 2015-7-16

@author: cheng.li
"""

import unittest
import csv
import os
from finpy.Risk import MovingAverage
from finpy.Risk import MovingPositiveAverage
from finpy.Risk import MovingNegativeAverage
from finpy.Risk import MovingSum
from finpy.Risk import MovingCountedPositive
from finpy.Risk import MovingCountedNegative
from finpy.Risk import MovingVariance
from finpy.Risk import MovingNegativeVariance
from finpy.Risk import MovingCorrelation
from finpy.Risk import MovingCorrelationMatrix


class TestStatefulAccumulators(unittest.TestCase):

    def testMovingAverager(self):

        window = 120
        total = 2500

        mv = MovingAverage(window, pNames='z')
        runningSum = 0.0
        con = []
        for i in range(total):
            value = float(i)
            con.append(value)
            mv.push(z=value)
            runningSum += value
            if i >= window:
                runningSum -= con[0]
                con = con[1:]

            if i >= window-1:
                expected = runningSum / window
                calculated = mv.result()
                self.assertAlmostEqual(calculated, expected, 15, "at index {0:d}\n"
                                                                 "Average expected:   {1:f}\n"
                                                                 "Average calculated: {2:f}".format(i, expected, calculated))

    def testMovingPositiveAverager(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/averagepostiveandnegative_random.csv')

        window = 20
        mv = MovingPositiveAverage(window, pNames='z')

        with open(filePath, 'r') as fileHandler:
            reader = csv.reader(fileHandler)

            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mv.push(z=float(row[1]))
                if i >= window:
                    expected = float(row[6])
                    calculated = mv.result()
                    self.assertAlmostEqual(calculated, expected, 8, "at index {0:d}\n"
                                                                    "Positive average expected:   {1:f}\n"
                                                                    "positive average calculated: {2:f}".format(i, expected, calculated))


    def testMovingNegativeAverager(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/averagepostiveandnegative_random.csv')

        window = 20
        mv = MovingNegativeAverage(window, pNames='z')

        with open(filePath, 'r') as fileHandler:
            reader = csv.reader(fileHandler)

            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mv.push(z=float(row[1]))
                if i >= window:
                    expected = float(row[7])
                    calculated = mv.result()
                    self.assertAlmostEqual(calculated, expected, 8, "at index {0:d}\n"
                                                                    "Positive average expected:   {1:f}\n"
                                                                    "positive average calculated: {2:f}".format(i, expected, calculated))

    def testMovingSum(self):
        window = 120
        total = 2500

        mv = MovingSum(window, pNames=['z'])
        runningSum = 0.0
        con = []
        for i in range(total):
            value = float(i)
            con.append(value)
            mv.push(z=value)
            runningSum += value

            if i >= window:
                runningSum -= con[0]
                con = con[1:]

            if i >= window - 1:
                expected = runningSum
                calculated = mv.result()
                self.assertAlmostEqual(calculated, expected, 15, "at index {0:d}\n"
                                                                 "Sum expected:   {1:f}\n"
                                                                 "Sum calculated: {2:f}".format(i, expected, calculated))

    def testMovingCountedPositive(self):
        window = 120
        total = 2500

        values = [1.0 if i % 2 else -1.0 for i in range(total)]
        mv = MovingCountedPositive(window, pNames='z')
        runningCount = 0
        con = []
        for i, value in enumerate(values):
            if i % 2:
                runningCount += 1
            con.append(i)
            mv.push(z=value)

            if i >= window:
                if con[0] % 2:
                    runningCount -= 1
                con = con[1:]

            if i >= window - 1:
                expected = runningCount
                calculated = mv.result()
                self.assertAlmostEqual(calculated, expected, 15, "at index {0:d}\n"
                                                                 "Counted positive expected:   {1:f}\n"
                                                                 "Counted positive calculated: {2:f}".format(i, expected, calculated))


    def testMovingCountedNegative(self):
        window = 120
        total = 2500

        values = [1.0 if i % 2 else -1.0 for i in range(total)]
        mv = MovingCountedNegative(window, pNames='z')
        runningCount = 0
        con = []
        for i, value in enumerate(values):
            if not i % 2:
                runningCount += 1
            con.append(i)
            mv.push(z=value)

            if i >= window:
                if not con[0] % 2:
                    runningCount -= 1
                con = con[1:]

            if i >= window - 1:
                expected = runningCount
                calculated = mv.result()
                self.assertAlmostEqual(calculated, expected, 15, "at index {0:d}\n"
                                                                 "Counted negative expected:   {1:f}\n"
                                                                 "Counted negative calculated: {2:f}".format(i, expected, calculated))

    def testMovingVariancer(self):
        window = 120
        total = 2500

        # Test moving population variance
        mv = MovingVariance(window, pNames='z', isPopulation=True)
        runningSum = 0.0
        runningSumSquare = 0.0
        con = []
        for i in range(total):
            value = float(i)
            con.append(value)
            mv.push(z=value)
            runningSum += value
            runningSumSquare += value * value
            if i >= window:
                runningSum -= con[0]
                runningSumSquare -= con[0] * con[0]
                con = con[1:]

            if i >= window-1:
                expected = (runningSumSquare - runningSum * runningSum / window) / window
                calculated = mv.result()
                self.assertAlmostEqual(calculated, expected, 15, "at index {0:d}\n"
                                                                 "Var expected:   {1:f}\n"
                                                                 "Var calculated: {2:f}".format(i, expected, calculated))

        # Test moving sample variance
        mv = MovingVariance(window, pNames='z', isPopulation=False)
        runningSum = 0.0
        runningSumSquare = 0.0
        con = []
        for i in range(total):
            value = float(i)
            con.append(value)
            mv.push(z=value)
            runningSum += value
            runningSumSquare += value * value
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
                                                                 "Var calculated: {2:f}".format(i, expected, calculated))

    def testMovingNegativeVariancer(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/negativevariance.csv')

        window = 20
        mv = MovingNegativeVariance(window,pNames='z')

        with open(filePath, 'r') as fileHandler:
            reader = csv.reader(fileHandler)
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mv.push(z=float(row[1]))
                if i >= window:
                    expected = float(row[6])
                    calculated = mv.result()
                    self.assertAlmostEqual(calculated, expected, 7, "at index {0:d}\n"
                                                                    "Negative variance expected:   {1:f}\n"
                                                                    "Negative variance calculated: {2:f}".format(i, expected, calculated))

    def testMovingCorrelation(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/correlation.csv')

        window = 120
        mv = MovingCorrelation(window, pNames=['z', 't'])

        with open(filePath, 'r') as fileHandler:
            reader = csv.reader(fileHandler)

            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mv.push(z=float(row[0]), t=float(row[1]))
                if i >= window:
                    expected = float(row[2])
                    calculated = mv.result()
                    self.assertAlmostEqual(calculated, expected, 8, "at index {0:d}\n"
                                                                    "Correlation expected:   {1:f}\n"
                                                                    "Correlation calculated: {2:f}".format(i, expected, calculated))

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

        mv = MovingCorrelationMatrix(window, pNames='samples')

        with open(filePath, 'r') as fileHandler:
            reader = csv.reader(fileHandler)

            reader = csv.reader(fileHandler)

            for i, row in enumerate(reader):
                row = [float(value) for value in row]
                mv.push(samples=row)
                if (i+1) == window:
                    calculated = mv.result()
                    for k, row in enumerate(first100Sample):
                        for j, corr in enumerate(row):
                            self.assertAlmostEqual(calculated[k][j], corr, 8, "First 100 sample correlation matrix different at ({0:d}, {1:d})\n"
                                                                               "Expected: {2:f}\n"
                                                                               "Calculated: {3:f}".format(k, j, corr, calculated[k][j]))
                if (i+1) == 1000:
                    calculated = mv.result()
                    for k, row in enumerate(last100Sample):
                        for j, corr in enumerate(row):
                            self.assertAlmostEqual(calculated[k][j], corr, 8, "Last 100 sample correlation matrix different at ({0:d}, {1:d})\n"
                                                                               "Expected: {2:f}\n"
                                                                               "Calculated: {3:f}".format(k, j, corr, calculated[k][j]))




