# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.pool import Pool
from . import dunning

__all__ = ['register']


def register():
    Pool.register(
        dunning.Level,
        module='account_dunning_mipago', type_='model')
    Pool.register(
        dunning.ProcessDunning,
        module='account_dunning_mipago', type_='wizard')
    Pool.register(
        dunning.MiPago,
        module='account_dunning_mipago', type_='report')
