# -*- coding: utf-8 -*-
u"""
Created on 2015-7-16

@author: cheng.li
"""

import csv
import unittest
import os
import numpy as np
from PyFin.Math.Accumulators.StatefulAccumulators import MovingSharp
from PyFin.Math.Accumulators.StatefulAccumulators import MovingSortino
from PyFin.Math.Accumulators.StatefulAccumulators import MovingDrawdown
from PyFin.Math.Accumulators.StatefulAccumulators import MovingMaxDrawdown


class TestPerformancers(unittest.TestCase):

    def testMovingSharp(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/sharp.csv')

        with open(filePath, 'r') as fileHandler:
            reader = csv.reader(fileHandler)
            mv = MovingSharp(20, x='ret', y='riskFree')

            for i, row in enumerate(reader):
                if i == 0:
                    continue
                data = {'ret': float(row[1]), 'riskFree': float(row[2])}
                mv.push(data)
                if i == 1:
                    self.assertTrue(np.isnan(mv.result()))
                if i >= 20:
                    calculated = mv.result()
                    expected = float(row[6])
                    self.assertAlmostEqual(calculated, expected, 7, "at index {0:d}\n"
                                                                    "Sharp expected:   {1:f}\n"
                                                                    "Sharp calculated: {2:f}".format(i, expected,
                                                                                                     calculated))

    def testMovingSortino(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/sortino.csv')

        window = 20

        with open(filePath, 'r') as fileHandler:
            reader = csv.reader(fileHandler)
            mv = MovingSortino(window, x='ret', y='riskFree')
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mv.push(dict(ret=float(row[2]), riskFree=float(row[3])))
                if i == 1:
                    self.assertTrue(np.isnan(mv.result()))
                if i >= window:
                    calculated = mv.result()
                    expected = float(row[10])
                    self.assertAlmostEqual(calculated, expected, 7, "at index {0:d}\n"
                                                                    "Sortino expected:   {1:f}\n"
                                                                    "Sortino calculated: {2:f}".format(i, expected,
                                                                                                       calculated))

    def testMovingDrawdownIncreasing(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/drawdown_increasing.csv')

        window = 20

        with open(filePath, 'r') as fileHandler:
            reader = csv.reader(fileHandler)
            mv = MovingDrawdown(window, x='ret')
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mv.push(dict(ret=float(row[1])))
                expectedDrawdown = float(row[2])
                calculatedDrawdown = mv.result()
                self.assertAlmostEqual(calculatedDrawdown, expectedDrawdown, 10, "at index {0:d}\n"
                                                                                 "Drawdown expected:   {1:f}\n"
                                                                                 "Drawdown calculated: {2:f}".format(i,
                                                                                                                     expectedDrawdown,
                                                                                                                     calculatedDrawdown))

    def testMovingDrawdownDecreasing(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/drawdown_decreasing.csv')

        window = 20

        with open(filePath, 'r') as fileHandler:
            reader = csv.reader(fileHandler)
            mv = MovingDrawdown(window, x='ret')
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mv.push(dict(ret=float(row[1])))
                expectedDrawdown = float(row[2])
                calculatedDrawdown = mv.result()
                self.assertAlmostEqual(calculatedDrawdown, expectedDrawdown, 10, "at index {0:d}\n"
                                                                                 "Drawdown expected:   {1:f}\n"
                                                                                 "Drawdown calculated: {2:f}".format(i,
                                                                                                                     expectedDrawdown,
                                                                                                                     calculatedDrawdown))

    def testMovingMaxDrawdownRandom(self):
        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/maxdrawdown_random.csv')

        window = 20

        with open(filePath, 'r') as fileHandler:
            reader = csv.reader(fileHandler)
            mv = MovingMaxDrawdown(window, x='ret')
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                mv.push(dict(ret=float(row[1])))
                expectedDrawdown = float(row[5])
                calculatedDrawdown = mv.result()
                self.assertAlmostEqual(calculatedDrawdown, expectedDrawdown, 7, "at index {0:d}\n"
                                                                                "Max drawdown expected:   {1:f}\n"
                                                                                "Max drawdown calculated: {2:f}".format(
                    i, expectedDrawdown, calculatedDrawdown))
