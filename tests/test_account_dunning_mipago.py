# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

import unittest
import doctest

from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import suite as test_suite
from trytond.tests.test_tryton import doctest_teardown
from trytond.tests.test_tryton import doctest_checker


class AccountDunningMiPagoTestCase(ModuleTestCase):
    'Test Account Dunning MiPago module'
    module = 'account_dunning_mipago'


def suite():
    suite = test_suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            AccountDunningMiPagoTestCase))
    suite.addTests(doctest.DocFileSuite(
            'scenario_account_dunning_mipago.rst',
            tearDown=doctest_teardown, encoding='utf-8',
            checker=doctest_checker,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
    return suite
