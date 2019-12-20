# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent consulting Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from datetime import datetime, timedelta
from odoo.tests.common import TransactionCase


class FSMAccountPaymentCase(TransactionCase):

    def setUp(self):
        super(FSMAccountPaymentCase, self).setUp()
        self.register_payments_model = self.env[
            'account.register.payments'].with_context(
            active_model='account.invoice')
        self.payment_method_manual_in = \
            self.env.ref("account.account_payment_method_manual_in")
        self.payment_model = self.env['account.payment']
        # create a Partner
        self.test_partner = self.env['res.partner'].\
            create({
                'name': 'Test Partner',
                'phone': '123',
                'email': 'tp@email.com',
                })
        # Create a location
        self.test_location = self.env['fsm.location'].\
            create({
                'name': 'Test Location',
                'phone': '123',
                'email': 'tp@email.com',
                'partner_id': self.test_loc_partner.id,
                'owner_id': self.test_loc_partner.id,
                'customer_id': self.test_loc_partner.id,
                })
        # Create a FSM order
        self.test_order = self.env['fsm.order'].create({
            'location_id': self.test_location.id,
            'date_start': datetime.today(),
            'date_end': datetime.today() + timedelta(hours=2),
            'request_early': datetime.today()
        })
        # Create an invoice
        self.test_invoice = self.env['account.invoice'].create({
            'partner_id': self.test_partner.id,
            'type': 'out_invoice',
            'date_invoice': datetime.today(),
            'invoice_line_ids': [(6, 0, [{
                'name': 'Test',
                'quantity': 1.00,
                'price_unit': 100.00,
                'fsm_order_id': self.test_order.id,
            }])],
            'fsm_order_ids': [(6, 0, [self.test_order.id])]
        })
        # Create a payment method
        self.bank_journal = self.env['account.journal'].create({
            'name': 'Bank',
            'type': 'bank',
            'code': 'BNK99',
        })

    def test_fsm_account_payment(self):
        self.test_invoice.action_invoice_open()

        ctx = {'active_model': 'account.invoice',
               'active_ids': [self.test_invoice.id]}
        register_payments = self.register_payments_model.with_context(ctx).create({
            'payment_date': datetime.today(),
            'journal_id': self.bank_journal.id,
            'payment_method_id': self.payment_method_manual_in.id,
        })
        register_payments.create_payments()
        payment = self.payment_model.search([], order="id desc", limit=1)

        self.assertAlmostEquals(payment.amount, 100)
        self.assertEqual(payment.state, 'posted')
        self.assertEqual(self.test_invoice.state, 'paid')
        self.assertEqual(self.test_invoice.fsm_order_ids,
                         payment.fsm_order_ids)
        res = self.env['fsm.order'].search([('payment_ids', 'in', payment.id)])
        self.assertEqual(len(res), 1)
