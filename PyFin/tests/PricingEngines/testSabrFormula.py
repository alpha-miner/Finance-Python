# -*- coding: utf-8 -*-
u"""
Created on 2017-1-6

@author: cheng.li
"""

import unittest
import numpy as np
from PyFin.PricingEngines import sabrVolatility
from PyFin.PricingEngines import sabrVolatilities
from PyFin.PricingEngines import sabrCalibration


class TestSabrFormula(unittest.TestCase):

    def setUp(self):
        self.strikes = np.array([0.] * 31)
        self.volatilities = np.array([0.] * 31)

        self.strikes[0] = 0.03
        self.strikes[1] = 0.032
        self.strikes[2] = 0.034
        self.strikes[3] = 0.036
        self.strikes[4] = 0.038
        self.strikes[5] = 0.04
        self.strikes[6] = 0.042
        self.strikes[7] = 0.044
        self.strikes[8] = 0.046
        self.strikes[9] = 0.048
        self.strikes[10] = 0.05
        self.strikes[11] = 0.052
        self.strikes[12] = 0.054
        self.strikes[13] = 0.056
        self.strikes[14] = 0.058
        self.strikes[15] = 0.06
        self.strikes[16] = 0.062
        self.strikes[17] = 0.064
        self.strikes[18] = 0.066
        self.strikes[19] = 0.068
        self.strikes[20] = 0.07
        self.strikes[21] = 0.072
        self.strikes[22] = 0.074
        self.strikes[23] = 0.076
        self.strikes[24] = 0.078
        self.strikes[25] = 0.08
        self.strikes[26] = 0.082
        self.strikes[27] = 0.084
        self.strikes[28] = 0.086
        self.strikes[29] = 0.088
        self.strikes[30] = 0.09

        self.volatilities[0] = 1.16725837321531
        self.volatilities[1] = 1.15226075991385
        self.volatilities[2] = 1.13829711098834
        self.volatilities[3] = 1.12524190877505
        self.volatilities[4] = 1.11299079244474
        self.volatilities[5] = 1.10145609357162
        self.volatilities[6] = 1.09056348513411
        self.volatilities[7] = 1.08024942745106
        self.volatilities[8] = 1.07045919457758
        self.volatilities[9] = 1.06114533019077
        self.volatilities[10] = 1.05226642581503
        self.volatilities[11] = 1.04378614411707
        self.volatilities[12] = 1.03567243073732
        self.volatilities[13] = 1.0278968727451
        self.volatilities[14] = 1.02043417226345
        self.volatilities[15] = 1.01326171139321
        self.volatilities[16] = 1.00635919013311
        self.volatilities[17] = 0.999708323124949
        self.volatilities[18] = 0.993292584155381
        self.volatilities[19] = 0.987096989695393
        self.volatilities[20] = 0.98110791455717
        self.volatilities[21] = 0.975312934134512
        self.volatilities[22] = 0.969700688771689
        self.volatilities[23] = 0.964260766651027
        self.volatilities[24] = 0.958983602256592
        self.volatilities[25] = 0.953860388001395
        self.volatilities[26] = 0.948882997029509
        self.volatilities[27] = 0.944043915545469
        self.volatilities[28] = 0.939336183299237
        self.volatilities[29] = 0.934753341079515
        self.volatilities[30] = 0.930289384251337

        self.expiry = 1.0
        self.forward = 0.039
        self.initialAlpha = 0.3
        self.initialBeta = 0.6
        self.initialNu = 0.02
        self.initialRho = 0.01

    def testSabrVolatility(self):
        for i, strike in enumerate(self.strikes):
            calculatedVol = sabrVolatility(strike,
                                           self.forward,
                                           self.expiry,
                                           self.initialAlpha,
                                           self.initialBeta,
                                           self.initialNu,
                                           self.initialRho)
            expectedVol = self.volatilities[i]
            self.assertAlmostEqual(calculatedVol, expectedVol)

    def testSabrVoaltilities(self):
        calculatedVols = sabrVolatilities(self.strikes,
                                          self.forward,
                                          self.expiry,
                                          self.initialAlpha,
                                          self.initialBeta,
                                          self.initialNu,
                                          self.initialRho)
        expectedVols = self.volatilities
        np.testing.assert_array_almost_equal(calculatedVols, expectedVols)

    def testSabrCalibrationWithTrf(self):
        x = sabrCalibration(self.strikes, self.volatilities, self.forward, self.expiry, 0.01, 0.01, 0.01, 0.01)
        calibratedParameters = x[0]

        calculatedVols = sabrVolatilities(self.strikes,
                                          self.forward,
                                          self.expiry,
                                          calibratedParameters[0],
                                          calibratedParameters[1],
                                          calibratedParameters[2],
                                          calibratedParameters[3])
        expectedVols = self.volatilities
        np.testing.assert_array_almost_equal(calculatedVols, expectedVols, 5)

    def testSabrCalibrationWithLM(self):
        x = sabrCalibration(self.strikes,
                            self.volatilities,
                            self.forward,
                            self.expiry,
                            0.01,
                            0.01,
                            0.01,
                            0.01,
                            method='lm')
        calibratedParameters = x[0]

        calculatedVols = sabrVolatilities(self.strikes,
                                          self.forward,
                                          self.expiry,
                                          calibratedParameters[0],
                                          calibratedParameters[1],
                                          calibratedParameters[2],
                                          calibratedParameters[3])
        expectedVols = self.volatilities
        np.testing.assert_array_almost_equal(calculatedVols, expectedVols, 4)

    def testSabrCalibrationWithFixedBeta(self):
        x = sabrCalibration(self.strikes,
                            self.volatilities,
                            self.forward,
                            self.expiry,
                            0.01,
                            self.initialBeta,
                            0.01,
                            0.01,
                            isFixedBeta=True)
        calibratedParameters = x[0]

        self.assertAlmostEqual(calibratedParameters[1], self.initialBeta)

        calculatedVols = sabrVolatilities(self.strikes,
                                          self.forward,
                                          self.expiry,
                                          calibratedParameters[0],
                                          calibratedParameters[1],
                                          calibratedParameters[2],
                                          calibratedParameters[3])

        expectedVols = self.volatilities
        np.testing.assert_array_almost_equal(calculatedVols, expectedVols, 4)
