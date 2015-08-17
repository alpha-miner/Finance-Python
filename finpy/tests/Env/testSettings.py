# -*- coding: utf-8 -*-
u"""
Created on 2015-7-15

@author: cheng.li
"""

import unittest
from finpy.DateUtilities import Date
from finpy.Env import Settings
from finpy.Env.Settings import SettingsFactory


class TestSettings(unittest.TestCase):
    def testEvaluationDate(self):
        referenceDate = Date(2015, 1, 1)
        Settings.evaluationDate = referenceDate
        self.assertEqual(Settings.evaluationDate, referenceDate, "Evaluation Date should be \n"
                                                                 "expected: {0}\n"
                                                                 "returned: {1}".format(referenceDate,
                                                                                        Settings.evaluationDate))

        # check wrong input
        with self.assertRaises(ValueError):
            Settings.evaluationDate = 2

        # settings should be a singleton
        secondeSettings = SettingsFactory()
        self.assertEqual(Settings.evaluationDate, secondeSettings.evaluationDate)

        # test forced building
        newSettings = SettingsFactory(forcedBuild=True)
        self.assertEqual(newSettings.evaluationDate, Date.todaysDate())
