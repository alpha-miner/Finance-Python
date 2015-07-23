# -*- coding: utf-8 -*-
u"""
Created on 2015-7-23

@author: cheng.li
"""

import unittest
import math

from finpy.Enums.OptionType import OptionType
from finpy.PricingEngines.BlackFormula import blackFormula
from finpy.PricingEngines.BlackFormula import blackFormulaImpliedStdDev


class TestBlackFormula(unittest.TestCase):

    def testBlackImpliedVol(self):

        forward = 1.0
        bpvol = 0.25
        tte = 10.0
        stdDev = bpvol * math.sqrt(tte)
        discount = 0.95

        dList = [-3.0, -2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 3.0]

        for d in dList:
            strike = forward * math.exp(d * bpvol * math.sqrt(tte))
            callPrem = blackFormula(OptionType.Call, strike, forward, stdDev, discount)
            impliedStdDev = blackFormulaImpliedStdDev(OptionType.Call, strike, forward, callPrem, discount)
            self.assertAlmostEqual(impliedStdDev, stdDev, 10)

            putPrem = blackFormula(OptionType.Put, strike, forward, stdDev, discount)
            impliedStdDev = blackFormulaImpliedStdDev(OptionType.Put, strike, forward, putPrem, discount)
            self.assertAlmostEqual(impliedStdDev, stdDev, 10)
