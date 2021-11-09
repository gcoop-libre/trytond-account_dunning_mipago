# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unicodedata
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateView, StateReport, Button
from trytond.report import Report
from trytond.pool import PoolMeta, Pool
from trytond.transaction import Transaction


class Level(metaclass=PoolMeta):
    __name__ = 'account.dunning.level'

    mipago = fields.Boolean("MiPago")


class ProcessDunning(metaclass=PoolMeta):
    __name__ = 'account.dunning.process'

    mipago = StateReport('account.dunning.mipago')

    @classmethod
    def __setup__(cls):
        super().__setup__()
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
            if not s:
                return ''
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


class MiPagoCustomerWizardStart(ModelView):
    'Dunning MiPago Customer'
    __name__ = 'account.dunning.mipago.customer_wizard.start'


class MiPagoCustomerWizard(Wizard):
    'Dunning MiPago Customer'
    __name__ = 'account.dunning.mipago.customer_wizard'

    start = StateView('account.dunning.mipago.customer_wizard.start',
        'account_dunning_mipago.mipago_customer_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Process', 'customer', 'tryton-ok', default=True),
        ])
    customer = StateReport('account.dunning.mipago.customer_report')

    def do_customer(self, action):
        pool = Pool()
        Dunning = pool.get('account.dunning')
        dunnings = Dunning.search([])
        ids = list(set([d.party.id for d in dunnings
            if not d.blocked
            and d.party
            and d.level.mipago]))
        if ids:
            return action, {
                'id': ids[0],
                'ids': ids,
                }


class MiPagoCustomerReport(Report):
    'Customers to Dunning MiPago'
    __name__ = 'account.dunning.mipago.customer_report'

    @classmethod
    def get_context(cls, records, data):

        def strip_accents(s):
            if not s:
                return ''
            return ''.join(c for c in unicodedata.normalize('NFD', s)
                if unicodedata.category(c) != 'Mn')

        context = super(MiPagoCustomerReport, cls).get_context(records, data)
        pool = Pool()
        Party = pool.get('party.party')
        parties = Party.browse(data['ids'])
        context['records'] = parties
        context['strip_accents'] = strip_accents
        context['_get_address'] = cls._get_address
        return context

    @classmethod
    def _get_address(cls, record):
        pool = Pool()
        Party = pool.get('party.party')
        if Party and isinstance(record, Party):
            contact = record.contact_mechanism_get(
                'email', usage='invoice')
            if contact and contact.email:
                return contact.email
