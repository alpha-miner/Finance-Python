# -*- coding: utf-8 -*-
u"""
Created on 2017-1-7

@author: cheng.li
"""

import unittest
import numpy as np
from PyFin.PricingEngines import sviVolatilities
from PyFin.PricingEngines import sviCalibration


class TestSVIInterpolation(unittest.TestCase):
    def setUp(self):
        self.strikes = np.array([0.] * 31)
        self.expiry = 1.0
        self.forward = 0.039

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

        self.initialA = -0.0410
        self.initialB = 0.1331
        self.initialSigma = 0.4153
        self.initialRho = 0.3060
        self.initialM = 0.3586

    def testSVICalibration(self):
        expectedVolatilities = sviVolatilities(self.strikes,
                                               self.forward,
                                               self.expiry,
                                               self.initialA,
                                               self.initialB,
                                               self.initialSigma,
                                               self.initialRho,
                                               self.initialM)

        x = sviCalibration(self.strikes, expectedVolatilities, self.forward, self.expiry, 0.01, 0.01, 0.01, 0.01, 0.01)
        calibratedParameters = x[0]
        calculatedVolatilities = sviVolatilities(self.strikes,
                                                 self.forward,
                                                 self.expiry,
                                                 calibratedParameters[0],
                                                 calibratedParameters[1],
                                                 calibratedParameters[2],
                                                 calibratedParameters[3],
                                                 calibratedParameters[4])

        np.testing.assert_array_almost_equal(expectedVolatilities, calculatedVolatilities)
