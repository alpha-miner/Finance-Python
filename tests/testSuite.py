# -*- coding: utf-8 -*-
u"""
Created on 2015-7-13

@author: cheng.li
"""

def test():

    import DateUtilities
    import Env
    import Math
    import Risk
    import PricingEngines
    import unittest

    suite = unittest.TestSuite()

    tests = unittest.TestLoader().loadTestsFromTestCase(DateUtilities.TestCalendar)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(DateUtilities.TestDate)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(DateUtilities.TestPeriod)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(Env.TestSettings)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(Math.TestDistribution)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(PricingEngines.TestBlackFormula)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(Risk.TestAccumulators)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(Risk.TestNormalizers)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(Risk.TestPerformancers)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(Risk.TestTimeseries)
    suite.addTests(tests)

    res = unittest.TextTestRunner(verbosity=3).run(suite)
    if len(res.errors) >= 1 or len(res.failures) >= 1:
        exit(-1)
    else:
        exit(0)

if __name__ == "__main__":
    test()


