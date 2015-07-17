# -*- coding: utf-8 -*-
u"""
Created on 2015-7-16

@author: cheng.li
"""

import pandas as pd
import unittest
import os
from finpy.Risk.Performancers import MovingSharp

class TestPerformancers(unittest.TestCase):

    def testMovingSharp(self):

        dirName = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(dirName, 'data/sharp.xlsx')

        res = pd.read_excel(filePath, 'Sheet1', index_col='index')

        ret = res['return']
        ben = res['benchmark']
        expectedSharps = res['sharp']

        mv = MovingSharp(20)

        for i in range(len(ret)):
            mv.push(ret[i], ben[i])
            if i >= 19:
                calculated = mv.result()
                expected = expectedSharps[i]
                self.assertAlmostEqual(calculated, expected, 14, "at index {0:d}\n"
                                                                 "Sharp expected:   {1:f}\n"
                                                                 "Sharp calculated: {2:f}".format(i, expected, calculated))

