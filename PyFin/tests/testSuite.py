# -*- coding: utf-8 -*-
u"""
Created on 2015-7-13

@author: cheng.li
"""

from simpleutils import add_parent_path

add_parent_path(__file__, 3)

from simpleutils import TestRunner
from simpleutils import CustomLogger
import PyFin.tests.api as api
import PyFin.tests.Analysis as Analysis
import PyFin.tests.CashFlows as CashFlows
import PyFin.tests.DateUtilities as DateUtilities
import PyFin.tests.Env as Env
import PyFin.tests.Math as Math
import PyFin.tests.POpt as POpt
import PyFin.tests.PricingEngines as PricingEngines
import PyFin.tests.Utilities as Utilities


if __name__ == "__main__":
    pyfin_logger = CustomLogger('FINANCE-PYTHON', 'info')
    test_runner = TestRunner([api.TestDateUtilities,
                              Analysis.TestDataProviders,
                              Analysis.TestSecurityValueHolders,
                              Analysis.TestCrossSectionValueHolder,
                              Analysis.TestSecurityValues,
                              Analysis.TestTransformer,
                              Analysis.TechnicalAnalysis.TestStatelessTechnicalAnalysis,
                              Analysis.TechnicalAnalysis.TestStatelessTechnicalAnalysis,
                              Analysis.TechnicalAnalysis.TestStatefulTechnicalAnalysis,
                              CashFlows.TestCashFlow,
                              CashFlows.TestInterestRate,
                              DateUtilities.TestCalendar,
                              DateUtilities.TestDate,
                              DateUtilities.TestPeriod,
                              DateUtilities.TestSchedule,
                              DateUtilities.TestDayCounter,
                              Env.TestSettings,
                              Math.Distributions.TestDistribution,
                              PricingEngines.TestBlackFormula,
                              PricingEngines.TestSabrFormula,
                              PricingEngines.TestSVIInterpolation,
                              Math.Accumulators.TestAccumulatorImpl,
                              Math.Accumulators.TestAccumulatorsArithmetic,
                              Math.Accumulators.TestStatefulAccumulators,
                              Math.Accumulators.TestStatelessAccumulators,
                              Math.Timeseries.TestNormalizers,
                              Math.Accumulators.TestPerformancers,
                              Math.Timeseries.TestTimeseries,
                              Math.RootFinder.TestBrent,
                              POpt.TestOptimizer,
                              Utilities.TestAsserts],
                             pyfin_logger)
    test_runner.run()
