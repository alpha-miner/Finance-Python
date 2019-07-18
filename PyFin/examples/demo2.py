from PyFin.Analysis.TechnicalAnalysis import SecurityMovingRank
from PyFin.Math.Accumulators.StatefulAccumulators import MovingCorrelation
# TSRANK(VOLUME,5)
expression1 = SecurityMovingRank(5, 'turnoverVol')
# TSRANK(HIGH,5)
expression2 = SecurityMovingRank(5, 'highPrice')

MovingCorrelation(5, expression1, expression2)