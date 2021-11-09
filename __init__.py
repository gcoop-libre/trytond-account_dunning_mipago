# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.pool import Pool
from . import dunning


def register():
    Pool.register(
        dunning.Level,
        dunning.MiPagoCustomerWizardStart,
        module='account_dunning_mipago', type_='model')
    Pool.register(
        dunning.ProcessDunning,
        dunning.MiPagoCustomerWizard,
        module='account_dunning_mipago', type_='wizard')
    Pool.register(
        dunning.MiPago,
        dunning.MiPagoCustomerReport,
        module='account_dunning_mipago', type_='report')
