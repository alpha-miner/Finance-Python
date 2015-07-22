# -*- coding: utf-8 -*-
u"""
Created on 2015-7-16

@author: cheng.li
"""

import csv
import unittest
import os
from finpy.Risk.Performancers import MovingSharp
from finpy.Risk.Performancers import MovingAlphaBeta
from finpy.Risk.Performancers import MovingDrawDown
from finpy.Risk.Performancers import MovingAverageDrawdown
from finpy.Risk.Performancers import MovingMaxDrawdown


class TestPerformancers(unittest.TestCase):

    def testMovingSharp(self):

        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/sharp.csv')

        with open(filePath, 'r') as fileHandler:
            reader = csv.reader(fileHandler)
            mv = MovingSharp(20)

            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mv.push(float(row[1]), float(row[2]))
                if i >= 20:
                    calculated = mv.result()
                    expected = float(row[6])
                    self.assertAlmostEqual(calculated, expected, 8, "at index {0:d}\n"
                                                                    "Sharp expected:   {1:f}\n"
                                                                    "Sharp calculated: {2:f}".format(i, expected, calculated))

    def testMovingAlphaBeta(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/alphabeta.csv')

        window = 120

        with open(filePath, 'r') as fileHandler:
            reader = csv.reader(fileHandler)
            mv = MovingAlphaBeta(window)
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mv.push(float(row[0]), float(row[1]), float(row[2]))
                if i >= window:
                    calculatedAlpha, calculatedBeta = mv.result()
                    expectedBeta = float(row[8])
                    self.assertAlmostEqual(calculatedBeta, expectedBeta, 8, "at index {0:d}\n"
                                                                            "Beta expected:   {1:f}\n"
                                                                            "Beta calculated: {2:f}".format(i, expectedBeta, calculatedBeta))
                    expectedAlpha = float(row[9])
                    self.assertAlmostEqual(calculatedAlpha, expectedAlpha, 8, "at index {0:d}\n"
                                                                              "Alpha expected:   {1:f}\n"
                                                                              "Alpha calculated: {2:f}".format(i, expectedAlpha, calculatedAlpha))

    def testMovingDrawdownIncreasing(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/drawdown_increasing.csv')

        window = 20

        with open(filePath, 'r') as fileHandler:
            reader = csv.reader(fileHandler)
            mv = MovingDrawDown(window)
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mv.push(float(row[1]))
                expectedDrawdown = float(row[2])
                calculatedDrawdown = mv.result()[0]
                self.assertAlmostEqual(calculatedDrawdown, expectedDrawdown, 10, "at index {0:d}\n"
                                                                                 "Drawdown expected:   {1:f}\n"
                                                                                 "Drawdown calculated: {2:f}".format(i, expectedDrawdown, calculatedDrawdown))

    def testMovingDrawdownDecreasing(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/drawdown_decreasing.csv')

        window = 20

        with open(filePath, 'r') as fileHandler:
            reader = csv.reader(fileHandler)
            mv = MovingDrawDown(window)
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mv.push(float(row[1]))
                expectedDrawdown = float(row[2])
                calculatedDrawdown = mv.result()[0]
                self.assertAlmostEqual(calculatedDrawdown, expectedDrawdown, 10, "at index {0:d}\n"
                                                                                 "Drawdown expected:   {1:f}\n"
                                                                                 "Drawdown calculated: {2:f}".format(i, expectedDrawdown, calculatedDrawdown))

    def testMovingDrawdownRandom(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/drawdown_random.csv')

        window = 20

        with open(filePath, 'r') as fileHandler:
            reader = csv.reader(fileHandler)
            mv = MovingDrawDown(window)
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mv.push(float(row[1]))
                expectedDrawdown = float(row[4])
                calculatedDrawdown = mv.result()[0]
                self.assertAlmostEqual(calculatedDrawdown, expectedDrawdown, 7, "at index {0:d}\n"
                                                                                "Drawdown expected:   {1:f}\n"
                                                                                "Drawdown calculated: {2:f}".format(i, expectedDrawdown, calculatedDrawdown))

    def testMovingAverageDrawdownRandom(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/averagedrawdown_random.csv')

        window = 20

        with open(filePath, 'r') as fileHandler:
            reader = csv.reader(fileHandler)
            mv = MovingAverageDrawdown(window)
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mv.push(float(row[1]))
                expectedDrawdown = float(row[5])
                calculatedDrawdown = mv.result()[0]
                self.assertAlmostEqual(calculatedDrawdown, expectedDrawdown, 7, "at index {0:d}\n"
                                                                                "Average drawdown expected:   {1:f}\n"
                                                                                "Average drawdown calculated: {2:f}".format(i, expectedDrawdown, calculatedDrawdown))

    def testMovingMaxDrawdwonRandom(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/maxdrawdown_random.csv')

        window = 20

        with open(filePath, 'r') as fileHandler:
            reader = csv.reader(fileHandler)
            mv = MovingMaxDrawdown(window)
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mv.push(float(row[1]))
                expectedDrawdown = float(row[5])
                calculatedDrawdown = mv.result()[0]
                self.assertAlmostEqual(calculatedDrawdown, expectedDrawdown, 7, "at index {0:d}\n"
                                                                                "Max drawdown expected:   {1:f}\n"
                                                                                "Max drawdown calculated: {2:f}".format(i, expectedDrawdown, calculatedDrawdown))

