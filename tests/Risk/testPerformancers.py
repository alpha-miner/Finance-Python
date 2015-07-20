# -*- coding: utf-8 -*-
u"""
Created on 2015-7-16

@author: cheng.li
"""

import csv
import unittest
import os
from finpy.Risk.Performancers import MovingSharp

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

