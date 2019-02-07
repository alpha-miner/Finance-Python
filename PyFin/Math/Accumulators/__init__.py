# -*- coding: utf-8 -*-
u"""
Created on 2015-8-8

@author: cheng.li
"""

from PyFin.Math.Accumulators.IAccumulators import Exp
from PyFin.Math.Accumulators.IAccumulators import Log
from PyFin.Math.Accumulators.IAccumulators import Sqrt
from PyFin.Math.Accumulators.IAccumulators import Sign
from PyFin.Math.Accumulators.IAccumulators import Abs
from PyFin.Math.Accumulators.IAccumulators import Pow
from PyFin.Math.Accumulators.IAccumulators import Acos
from PyFin.Math.Accumulators.IAccumulators import Acosh
from PyFin.Math.Accumulators.IAccumulators import Asin
from PyFin.Math.Accumulators.IAccumulators import Asinh
from PyFin.Math.Accumulators.IAccumulators import NormInv
from PyFin.Math.Accumulators.IAccumulators import Current
from PyFin.Math.Accumulators.IAccumulators import Latest
from PyFin.Math.Accumulators.IAccumulators import Ceil
from PyFin.Math.Accumulators.IAccumulators import Floor
from PyFin.Math.Accumulators.IAccumulators import Round
from PyFin.Math.Accumulators.IAccumulators import Identity
from PyFin.Math.Accumulators.IAccumulators import IIF
from PyFin.Math.Accumulators.IAccumulators import Sign
from PyFin.Math.Accumulators.IAccumulators import Negative

from PyFin.Math.Accumulators.StatelessAccumulators import Diff
from PyFin.Math.Accumulators.StatelessAccumulators import SimpleReturn
from PyFin.Math.Accumulators.StatelessAccumulators import LogReturn
from PyFin.Math.Accumulators.StatelessAccumulators import PositivePart
from PyFin.Math.Accumulators.StatelessAccumulators import NegativePart
from PyFin.Math.Accumulators.StatelessAccumulators import Max
from PyFin.Math.Accumulators.StatelessAccumulators import Maximum
from PyFin.Math.Accumulators.StatelessAccumulators import Min
from PyFin.Math.Accumulators.StatelessAccumulators import Minimum
from PyFin.Math.Accumulators.StatelessAccumulators import Sum
from PyFin.Math.Accumulators.StatelessAccumulators import Average
from PyFin.Math.Accumulators.StatelessAccumulators import XAverage
from PyFin.Math.Accumulators.StatelessAccumulators import Variance
from PyFin.Math.Accumulators.StatelessAccumulators import Product

from PyFin.Math.Accumulators.StatefulAccumulators import Shift
from PyFin.Math.Accumulators.StatefulAccumulators import Delta
from PyFin.Math.Accumulators.StatefulAccumulators import MovingAverage
from PyFin.Math.Accumulators.StatefulAccumulators import MovingDecay
from PyFin.Math.Accumulators.StatefulAccumulators import MovingPositiveAverage
from PyFin.Math.Accumulators.StatefulAccumulators import MovingNegativeAverage
from PyFin.Math.Accumulators.StatefulAccumulators import MovingPositiveDifferenceAverage
from PyFin.Math.Accumulators.StatefulAccumulators import MovingNegativeDifferenceAverage
from PyFin.Math.Accumulators.StatefulAccumulators import MovingRSI
from PyFin.Math.Accumulators.StatefulAccumulators import MovingSum
from PyFin.Math.Accumulators.StatefulAccumulators import MovingCountedPositive
from PyFin.Math.Accumulators.StatefulAccumulators import MovingCountedNegative
from PyFin.Math.Accumulators.StatefulAccumulators import MovingVariance
from PyFin.Math.Accumulators.StatefulAccumulators import MovingStandardDeviation
from PyFin.Math.Accumulators.StatefulAccumulators import MovingNegativeVariance
from PyFin.Math.Accumulators.StatefulAccumulators import MovingCorrelation
from PyFin.Math.Accumulators.StatefulAccumulators import MovingMax
from PyFin.Math.Accumulators.StatefulAccumulators import MovingArgMax
from PyFin.Math.Accumulators.StatefulAccumulators import MovingMin
from PyFin.Math.Accumulators.StatefulAccumulators import MovingArgMin
from PyFin.Math.Accumulators.StatefulAccumulators import MovingRank
from PyFin.Math.Accumulators.StatefulAccumulators import MovingQuantile
from PyFin.Math.Accumulators.StatefulAccumulators import MovingAllTrue
from PyFin.Math.Accumulators.StatefulAccumulators import MovingAnyTrue
from PyFin.Math.Accumulators.StatefulAccumulators import MovingProduct
from PyFin.Math.Accumulators.StatefulAccumulators import MACD
from PyFin.Math.Accumulators.StatefulAccumulators import MovingRank
from PyFin.Math.Accumulators.StatefulAccumulators import MovingLogReturn
from PyFin.Math.Accumulators.StatefulAccumulators import MovingResidue
from PyFin.Math.Accumulators.StatefulAccumulators import MovingSharp
from PyFin.Math.Accumulators.StatefulAccumulators import MovingSortino
from PyFin.Math.Accumulators.StatefulAccumulators import MovingDrawdown
from PyFin.Math.Accumulators.StatefulAccumulators import MovingMaxDrawdown


__all__ = ["Exp",
           "Log",
           "Sqrt",
           "Sign",
           "Negative",
           "Abs",
           "Pow",
           "Acos",
           "Acosh",
           "Asin",
           "Asinh",
           "NormInv",
           "Current",
           "Latest",
           "Sign",
           "Diff",
           "SimpleReturn",
           "LogReturn",
           "PositivePart",
           "NegativePart",
           "Max",
           "Maximum",
           "Min",
           "Minimum",
           "Sum",
           "Average",
           "XAverage",
           "MACD",
           "Variance",
           "Shift",
           "Delta",
           "IIF",
           "Identity",
           "MovingAverage",
           "MovingDecay",
           "MovingPositiveAverage",
           "MovingNegativeAverage",
           "MovingPositiveDifferenceAverage",
           "MovingNegativeDifferenceAverage",
           "MovingRSI",
           "MovingSum",
           "MovingCountedPositive",
           "MovingCountedNegative",
           "MovingNegativeVariance",
           "MovingCorrelation",
           "MovingMax",
           "MovingArgMax",
           "MovingMin",
           "MovingArgMin",
           "MovingRank",
           "MovingQuantile",
           "MovingAllTrue",
           "MovingAnyTrue",
           "MovingVariance",
           "MovingStandardDeviation",
           "MovingLogReturn",
           "MovingResidue",
           "MovingSharp",
           "MovingSortino",
           "MovingDrawdown",
           "MovingMaxDrawdown",
           "Product",
           "MovingProduct"]
