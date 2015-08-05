# -*- coding: utf-8 -*-
u"""
Created on 2015-7-13

@author: cheng.li
"""

import sys
import unittest
import finpy.tests.API as API
import finpy.tests.DateUtilities as DateUtilities
import finpy.tests.Env as Env
import finpy.tests.Math as Math
import finpy.tests.Risk as Risk
import finpy.tests.PricingEngines as PricingEngines


def test():
    print('Python ' + sys.version)
    suite = unittest.TestSuite()

    tests = unittest.TestLoader().loadTestsFromTestCase(API.TestDateUtilities)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(DateUtilities.TestCalendar)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(DateUtilities.TestDate)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(DateUtilities.TestPeriod)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(DateUtilities.TestSchedule)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(Env.TestSettings)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(Math.TestDistribution)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(Math.TestErrorFunction)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(PricingEngines.TestBlackFormula)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(Risk.TestAccumulatorsArithmetic)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(Risk.TestStatefulAccumulators)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(Risk.TestStatelessAccumulators)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(Risk.TestNormalizers)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(Risk.TestPerformancers)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(Risk.TestTimeseries)
    suite.addTests(tests)

    res = unittest.TextTestRunner(verbosity=3).run(suite)
    if len(res.errors) >= 1 or len(res.failures) >= 1:
        sys.exit(-1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    test()


