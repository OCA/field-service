# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as common
from datetime import datetime, timedelta


class TestDayrouteAccount(common.TransactionCase):

    def setUp(self):
        super(TestDayrouteAccount, self).setUp()

        self.Partner = self.env['res.partner']
        self.user_type_payable = self.env.ref(
            'account.data_account_type_payable')
        self.account_payable = self.env['account.account'].create({
            'code': 'NC1110',
            'name': 'Test Payable Account',
            'user_type_id': self.user_type_payable.id,
            'reconcile': True
        })
        self.user_type_receivable = self.env.ref(
            'account.data_account_type_receivable')
        self.account_receivable = self.env['account.account'].create({
            'code': 'NC1111',
            'name': 'Test Receivable Account',
            'user_type_id': self.user_type_receivable.id,
            'reconcile': True
        })
        self.test_analytic = self.env.ref('analytic.analytic_administratif')

        # Create a customer
        self.partner_customer_usd = self.Partner.create({
            'name': 'Customer from the North',
            'email': 'customer.usd@north.com',
            'customer': True,
            'property_account_payable_id': self.account_payable.id,
            'property_account_receivable_id': self.account_receivable.id,
        })

        user_type_income = self.env.ref(
            'account.data_account_type_direct_costs')
        self.account_income_product = self.env['account.account'].create({
            'code': 'INCOME_PROD111',
            'name': 'Icome - Test Account',
            'user_type_id': user_type_income.id,
        })
        # Create category
        self.product_category = self.env['product.category'].create({
            'name': 'Product Category with Income account',
            'property_account_income_categ_id': self.account_income_product.id
        })
        uom_unit = self.env.ref('uom.product_uom_unit')
        # Create a product
        self.product_order = self.env['product.product'].create({
            'name': "Zed+ Antivirus",
            'standard_price': 235.0,
            'list_price': 280.0,
            'type': 'product',
            'uom_id': uom_unit.id,
            'uom_po_id': uom_unit.id,
            'invoice_policy': 'order',
            'expense_policy': 'no',
            'default_code': 'PROD_ORDER',
            'service_type': 'manual',
            'taxes_id': False,
            'categ_id': self.product_category.id,
        })
        # Create a worker
        self.fsm_worker = self.env['fsm.person'].create(
            {'name': 'Test Worker'})
        self.company = self.env.ref('base.main_company')
        self.payment_method_manual_in = self.env.ref(
            "account.account_payment_method_manual_in")
        # Create a Journal
        self.bank_journal = self.env['account.journal'].create(
            {'name': 'Bank US', 'type': 'bank', 'code': 'BNK68',
             'currency_id': self.company.currency_id.id})

        # create a Res Partner
        self.test_partner = self.env['res.partner'].\
            create({
                'name': 'Test Partner',
                'phone': '123',
                'email': 'tp@email.com',
            })
        # create a Res Partner to be converted to FSM Location/Person
        self.test_loc_partner = self.env['res.partner'].\
            create({
                'name': 'Test Loc Partner',
                'phone': 'ABC',
                'email': 'tlp@email.com',
            })
        self.test_loc_partner2 = self.env['res.partner'].\
            create({
                'name': 'Test Loc Partner 2',
                'phone': '123',
                'email': 'tlp@example.com',
            })
        # create expected FSM Location to compare to converted FSM Location
        self.test_location = self.env['fsm.location'].\
            create({
                'name': 'Test Location',
                'phone': '123',
                'email': 'tp@email.com',
                'partner_id': self.test_loc_partner.id,
                'owner_id': self.test_loc_partner.id,
                'customer_id': self.test_loc_partner.id,
                'analytic_account_id': self.test_analytic.id
            })
        self.account_income = self.env['account.account'].create({
            'code': 'X1112',
            'name': 'Sale - Test Account',
            'user_type_id': self.env.ref(
                'account.data_account_type_direct_costs').id
        })

    def test_dayroute_account(self):
        # Create a FSM order
        self.test_order = self.env['fsm.order'].create({
            'location_id': self.test_location.id,
            'date_start': datetime.today(),
            'date_end': datetime.today() + timedelta(hours=2),
            'request_early': datetime.today(),
            'person_id': self.fsm_worker.id,
            'scheduled_date_start': '2019-12-26 11:00:00'
        })
        # Create an invoice
        self.test_invoice = self.env['account.invoice'].create({
            'partner_id': self.test_partner.id,
            'type': 'out_invoice',
            'date_invoice': datetime.today().date(),
            'invoice_line_ids': [(0, 0, {
                'name': self.product_order.name,
                'product_id': self.product_order.id,
                'quantity': 2.00,
                'price_unit': self.product_order.list_price,
                'fsm_order_id': self.test_order.id,
                'account_id': self.account_income.id})],
            'fsm_order_ids': [(6, 0, [self.test_order.id])]
        })

        self.test_invoice.action_invoice_open()
        # Creating payment for invoice
        payment = self.env['account.payment'].create({
            'payment_date': '2019-12-26',
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'amount': self.test_invoice.amount_total,
            'currency_id': self.company.currency_id.id,
            'journal_id': self.bank_journal.id,
            'payment_method_id': self.payment_method_manual_in.id,
            'invoice_ids': [(4, self.test_invoice.id)]

        })
        # Validating the payment
        payment.action_validate_invoice_payment()
        # A dayroute payment will be created.
        for dayroute_payment in\
                self.test_order.dayroute_id.dayroute_payment_ids:
            self.assertTrue(dayroute_payment)
            self.assertEqual(dayroute_payment.amount_collected, 560.0)
            dayroute_payment.amount_counted = 500
            self.assertEqual(dayroute_payment.difference, 60.0)
            dayroute_close_state = self.env['fsm.stage'].search(
                ["&", ("stage_type", "=", "route"),
                 ("is_closed", "=", True)])
            # Closing Day Route
            self.test_order.dayroute_id.write(
                {'stage_id': dayroute_close_state.id})
            # A journal entry will be created.
            self.assertTrue(dayroute_payment.move_id)
            self.assertEqual(dayroute_payment.move_id.amount,
                             dayroute_payment.difference)
