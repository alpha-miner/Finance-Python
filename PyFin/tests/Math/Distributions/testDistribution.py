# -*- coding: utf-8 -*-
u"""
Created on 2015-7-23

@author: cheng.li
"""

import unittest
import math
import copy
import tempfile
import pickle
import os
from PyFin.Math.Distributions import InverseCumulativeNormal
from PyFin.Math.Distributions import NormalDistribution
from PyFin.Math.Distributions import CumulativeNormalDistribution

average = 1.0
sigma = 2.0


def gaussian(x):
    normFact = sigma * math.sqrt(2.0 * math.pi)
    dx = x - average
    return math.exp(-dx * dx / (2.0 * sigma * sigma)) / normFact


def gaussianDerivative(x):
    normFact = sigma * sigma * sigma * math.sqrt(2.0 * math.pi)
    dx = x - average
    return -dx * math.exp(-dx * dx / (2.0 * sigma * sigma)) / normFact


class TestDistribution(unittest.TestCase):

    def testNormal(self):
        invCumStandardNormal = InverseCumulativeNormal()

        check = invCumStandardNormal(0.5)
        self.assertAlmostEqual(check, 0.0, 10, "inverse cumulative of the standard normal at 0.5 is {0:f}"
                                               "\n instead of zero: something is wrong!".format(check))

        normal = NormalDistribution(average, sigma)
        cum = CumulativeNormalDistribution(average, sigma)
        invCum = InverseCumulativeNormal(average, sigma)
        invCumAcc = InverseCumulativeNormal(average, sigma, fullAccuracy=True)

        numberOfStandardDeviation = 6
        xMin = average - numberOfStandardDeviation * sigma
        xMax = average + numberOfStandardDeviation * sigma

        N = 100001
        h = (xMax - xMin) / (N - 1)

        x = [xMin + i * h for i in range(N)]
        y = [gaussian(v) for v in x]
        yd = [gaussianDerivative(v) for v in x]

        temp = [normal(v) for v in x]
        for i, (expected, calculated) in enumerate(zip(y, temp)):
            self.assertAlmostEqual(expected, calculated, 15, "at index {0:d}\n"
                                                             "Expected:  {1:f}\n"
                                                             "Calculated: {2:f}".format(i, expected, calculated))

        temp = [cum(v) for v in x]
        temp = [invCum(v) for v in temp]

        for i, (expected, calculated) in enumerate(zip(x, temp)):
            self.assertAlmostEqual(expected, calculated, 7, "at index {0:d}\n"
                                                            "Expected gaussian:  {1:f}\n"
                                                            "Calculated Gaussian: {2:f}".format(i, expected,
                                                                                                calculated))

        temp = [cum(v) for v in x]
        temp = [invCumAcc(v) for v in temp]

        for i, (expected, calculated) in enumerate(zip(x, temp)):
            self.assertAlmostEqual(expected, calculated, 7, "at index {0:d}\n"
                                                            "Expected gaussian:  {1:.9f}\n"
                                                            "Calculated Gaussian: {2:.9f}".format(i, expected,
                                                                                                  calculated))

        temp = [cum.derivative(v) for v in x]
        for i, (expected, calculated) in enumerate(zip(y, temp)):
            self.assertAlmostEqual(expected, calculated, 15, "at index {0:d}\n"
                                                             "Expected:  {1:f}\n"
                                                             "Calculated: {2:f}".format(i, expected, calculated))

        temp = [normal.derivative(v) for v in x]
        for i, (expected, calculated) in enumerate(zip(yd, temp)):
            self.assertAlmostEqual(expected, calculated, 15, "at index {0:d}\n"
                                                             "Expected:  {1:f}\n"
                                                             "Calculated: {2:f}".format(i, expected, calculated))

        # test nan value returning
        self.assertTrue(math.isnan(invCum(-0.5)))

    def testNormalDistributionCopy(self):
        norm = NormalDistribution(average, sigma)
        copied = copy.deepcopy(norm)

        self.assertEqual(norm, copied)

    def testNormalDistributionPickle(self):
        benchmark_norm = NormalDistribution(average, sigma)

        f = tempfile.NamedTemporaryFile('w+b', delete=False)
        pickle.dump(benchmark_norm, f)
        f.close()

        with open(f.name, 'rb') as f2:
            pickled_norm = pickle.load(f2)
            self.assertEqual(benchmark_norm, pickled_norm)

        os.unlink(f.name)

    def testCumulativeNormalDistribution(self):
        norm = CumulativeNormalDistribution(average, sigma)
        copied = copy.deepcopy(norm)

        self.assertEqual(norm, copied)

    def testCumulativeNormalDistributionPickle(self):
        benchmark_norm = CumulativeNormalDistribution(average, sigma)

        f = tempfile.NamedTemporaryFile('w+b', delete=False)
        pickle.dump(benchmark_norm, f)
        f.close()

        with open(f.name, 'rb') as f2:
            pickled_norm = pickle.load(f2)
            self.assertEqual(benchmark_norm, pickled_norm)

        os.unlink(f.name)

    def testInverseCumulativeNormal(self):
        norm = InverseCumulativeNormal(average, sigma, True)
        copied = copy.deepcopy(norm)

        self.assertEqual(norm, copied)

    def testInverseCumulativeNormalPickle(self):
        benchmark_norm = InverseCumulativeNormal(average, sigma)

        f = tempfile.NamedTemporaryFile('w+b', delete=False)
        pickle.dump(benchmark_norm, f)
        f.close()

        with open(f.name, 'rb') as f2:
            pickled_norm = pickle.load(f2)
            self.assertEqual(benchmark_norm, pickled_norm)