# -*- coding: utf-8 -*-
u"""
Created on 2017-1-17

@author: cheng.li
"""

import math
import numpy as np


def gediVolatility(strike, forward, expiry, atmVol, skew, kurt):

    moneyness = math.log(strike / forward) / math.sqrt(expiry)
    s = math.atan(moneyness)

    return atmVol + s * skew + kurt * (s ** 2)


def gediVolatilities(strikes, forward, expiry, atmVol, skew, kurt):
    return np.array([gediVolatility(strike, forward, expiry, atmVol, skew, kurt) for strike in strikes])