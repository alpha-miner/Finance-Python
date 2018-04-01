# -*- coding: utf-8 -*-
u"""
Created on 2016-4-1

@author: cheng.li
"""

import math
from PyFin.Math.Accumulators import MovingSharp
from PyFin.Math.Accumulators import MovingSortino


def calculate_annualized_return(returns, multplier=50):
    return returns.mean() * multplier


def calculate_volatility(returns, multplier=50):
    return returns.std(ddof=1) * math.sqrt(multplier)


def calculate_sharp(returns, multplier=50):
    msharp = MovingSharp(len(returns), x='ret', y='riskFree')
    for ret in returns:
        msharp.push({'ret': ret, 'riskFree': 0.})
    return msharp.value * math.sqrt(multplier)


def calculate_sortino(returns, multplier=50):
    msortino = MovingSortino(len(returns))
    for ret in returns:
        msortino.push({'ret': ret, 'riskFree': 0.})
    return msortino.value * math.sqrt(multplier)
