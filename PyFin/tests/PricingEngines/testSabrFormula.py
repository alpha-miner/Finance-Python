# -*- coding: utf-8 -*-
u"""
Created on 2017-1-6

@author: cheng.li
"""

import unittest
from PyFin.PricingEngines import sabrVolatility


class TestSabrFormula(unittest.TestCase):

    def testSabrVolatily(self):
        strikes = [0.] * 31
        volatilities = [0.] * 31

        strikes[0] = 0.03
        strikes[1] = 0.032
        strikes[2] = 0.034
        strikes[3] = 0.036
        strikes[4] = 0.038
        strikes[5] = 0.04
        strikes[6] = 0.042
        strikes[7] = 0.044
        strikes[8] = 0.046
        strikes[9] = 0.048
        strikes[10] = 0.05
        strikes[11] = 0.052
        strikes[12] = 0.054
        strikes[13] = 0.056
        strikes[14] = 0.058
        strikes[15] = 0.06
        strikes[16] = 0.062
        strikes[17] = 0.064
        strikes[18] = 0.066
        strikes[19] = 0.068
        strikes[20] = 0.07
        strikes[21] = 0.072
        strikes[22] = 0.074
        strikes[23] = 0.076
        strikes[24] = 0.078
        strikes[25] = 0.08
        strikes[26] = 0.082
        strikes[27] = 0.084
        strikes[28] = 0.086
        strikes[29] = 0.088
        strikes[30] = 0.09

        volatilities[0] = 1.16725837321531
        volatilities[1] = 1.15226075991385
        volatilities[2] = 1.13829711098834
        volatilities[3] = 1.12524190877505
        volatilities[4] = 1.11299079244474
        volatilities[5] = 1.10145609357162
        volatilities[6] = 1.09056348513411
        volatilities[7] = 1.08024942745106
        volatilities[8] = 1.07045919457758
        volatilities[9] = 1.06114533019077
        volatilities[10] = 1.05226642581503
        volatilities[11] = 1.04378614411707
        volatilities[12] = 1.03567243073732
        volatilities[13] = 1.0278968727451
        volatilities[14] = 1.02043417226345
        volatilities[15] = 1.01326171139321
        volatilities[16] = 1.00635919013311
        volatilities[17] = 0.999708323124949
        volatilities[18] = 0.993292584155381
        volatilities[19] = 0.987096989695393
        volatilities[20] = 0.98110791455717
        volatilities[21] = 0.975312934134512
        volatilities[22] = 0.969700688771689
        volatilities[23] = 0.964260766651027
        volatilities[24] = 0.958983602256592
        volatilities[25] = 0.953860388001395
        volatilities[26] = 0.948882997029509
        volatilities[27] = 0.944043915545469
        volatilities[28] = 0.939336183299237
        volatilities[29] = 0.934753341079515
        volatilities[30] = 0.930289384251337

        expiry = 1.0
        forward = 0.039
        initialAlpha = 0.3
        initialBeta = 0.6
        initialNu = 0.02
        initialRho = 0.01

        for i, strike in enumerate(strikes):
            calculatedVol = sabrVolatility(strike, forward, expiry, initialAlpha, initialBeta, initialNu, initialRho)
            expectedVol = volatilities[i]
            self.assertAlmostEqual(calculatedVol, expectedVol)