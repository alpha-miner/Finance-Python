# -*- coding: utf-8 -*-
u"""
Created on 2015-7-23

@author: cheng.li
"""

import unittest
import math
from PyFin.Enums.OptionType import OptionType
from PyFin.PricingEngines.BlackFormula import bachelierFormula
from PyFin.PricingEngines.BlackFormula import bachelierFormulaImpliedVol
from PyFin.PricingEngines.BlackFormula import blackFormula
from PyFin.PricingEngines.BlackFormula import blackFormula2
from PyFin.PricingEngines.BlackFormula import blackFormulaImpliedStdDev
from PyFin.PricingEngines.BlackFormula import blackFormulaImpliedVol


class TestBlackFormula(unittest.TestCase):

    def testBlackBasic(self):
        strike = 1.0
        forward = 1.2
        stdDev = 0.2
        discount = 0.95

        expected = discount * (forward - strike)
        calculated = blackFormula(OptionType.Call, strike, forward, 0.0, discount)
        self.assertAlmostEqual(expected, calculated, 15)

        expected = discount * forward
        calculated = blackFormula(OptionType.Call, 0.0, forward, stdDev, discount)
        self.assertAlmostEqual(expected, calculated, 15)

    def testBachelierBasics(self):
        strike = 1.0
        forward = 1.2
        discount = 0.95

        expected = discount * (forward - strike)
        calculated = bachelierFormula(OptionType.Call, strike, forward, 0.0, discount)
        self.assertAlmostEqual(expected, calculated, 15)

    def testBlackImpliedStdDev(self):
        forward = 1.0
        bpvol = 0.25
        tte = 10.0
        stdDev = bpvol * math.sqrt(tte)
        discount = math.exp(-0.05 * tte)

        dList = [-3.0, -2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 3.0]

        for d in dList:
            strike = forward * math.exp(d * bpvol * math.sqrt(tte))
            callPrem = blackFormula(OptionType.Call, strike, forward, stdDev, discount)
            impliedStdDev = blackFormulaImpliedStdDev(OptionType.Call, strike, forward, callPrem, discount)
            self.assertAlmostEqual(impliedStdDev, stdDev, 8)

            putPrem = blackFormula(OptionType.Put, strike, forward, stdDev, discount)
            impliedStdDev = blackFormulaImpliedStdDev(OptionType.Put, strike, forward, putPrem, discount)
            self.assertAlmostEqual(impliedStdDev, stdDev, 8)

    def testBlackImpliedVol(self):
        forward = 1.0
        bpvol = 0.25
        tte = 10.0
        riskFree = 0.05

        dList = [-3.0, -2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 3.0]

        for d in dList:
            strike = forward * math.exp(d * bpvol * math.sqrt(tte))
            callPrem = blackFormula2(OptionType.Call, strike, forward, tte, bpvol, riskFree)
            impliedVol = blackFormulaImpliedVol(OptionType.Call, strike, forward, tte, callPrem, riskFree)
            self.assertAlmostEqual(impliedVol, bpvol, 8)

            putPrem = blackFormula2(OptionType.Put, strike, forward, tte, bpvol, riskFree)
            impliedVol = blackFormulaImpliedVol(OptionType.Put, strike, forward, tte, putPrem, riskFree)
            self.assertAlmostEqual(impliedVol, bpvol, 8)

    def testBachelierImpliedVol(self):
        forward = 1.0
        bpvol = 0.01
        tte = 10.0
        r = 0.03

        dList = [-3.0, -2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 3.0]

        for d in dList:
            strike = forward + d * bpvol * math.sqrt(tte)
            callPrem = bachelierFormula(OptionType.Call, strike, forward, bpvol * math.sqrt(tte), math.exp(-r * tte))
            impliedBpVol = bachelierFormulaImpliedVol(OptionType.Call, strike, forward, tte, callPrem,
                                                      math.exp(-r * tte))
            self.assertAlmostEqual(impliedBpVol, bpvol, 12)

            callPrem = bachelierFormula(OptionType.Put, strike, forward, bpvol * math.sqrt(tte), math.exp(-r * tte))
            impliedBpVol = bachelierFormulaImpliedVol(OptionType.Put, strike, forward, tte, callPrem,
                                                      math.exp(-r * tte))
            self.assertAlmostEqual(impliedBpVol, bpvol, 12)
