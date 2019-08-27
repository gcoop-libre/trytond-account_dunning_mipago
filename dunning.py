# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.wizard import StateReport
from trytond.report import Report
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.tools import grouped_slice

__all__ = ['Level', 'ProcessDunning', 'MiPago']


class Level(metaclass=PoolMeta):
    __name__ = 'account.dunning.level'
    mipago = fields.Boolean("MiPago")


class ProcessDunning(metaclass=PoolMeta):
    __name__ = 'account.dunning.process'
    mipago = StateReport('account.dunning.mipago')

    @classmethod
    def __setup__(cls):
        super(ProcessDunning, cls).__setup__()
        cls._actions.append('mipago')

    def do_mipago(self, action):
        pool = Pool()
        Dunning = pool.get('account.dunning')
        dunnings = Dunning.browse(Transaction().context['active_ids'])
        ids = [d.id for d in dunnings
            if d.state == 'waiting'
            and not d.blocked
            and d.party
            and d.level.mipago]
        if ids:
            return action, {
                'id': ids[0],
                'ids': ids,
                }

    def transition_mipago(self):
        return self.next_state('mipago')


class MiPago(Report):
    'Dunning MiPago'
    __name__ = 'account.dunning.mipago'

    @classmethod
    def get_context(cls, records, data):

        def format_decimal(n, include_sign=False):
            if not isinstance(n, Decimal):
                n = Decimal(n)
            sign = ''
            if include_sign:
                sign = 'N' if n < 0 else ''
            return sign + ('{0:.2f}'.format(abs(n)))


        def strip_accents(s):
            return ''.join(c for c in unicodedata.normalize('NFD', s)
                if unicodedata.category(c) != 'Mn')

        context = super(MiPago, cls).get_context(records, data)
        pool = Pool()
        Date = pool.get('ir.date')

        dunnings = [d for d in records
            if d.state == 'waiting'
            and not d.blocked
            and d.party]
        context['records'] = dunnings
        context['maturity_date'] = Date.today() + relativedelta(months=1)
        context['format_decimal'] = format_decimal
        context['strip_accents'] = strip_accents
        return context
