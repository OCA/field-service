# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as common


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
            'field_service_tracking': 'sale'
        })
        # Create a location
        self.location = self.env.ref('fieldservice.location_1')
        self.location.analytic_account_id = self.env.ref(
            'analytic.analytic_administratif')
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

    def test_dayroute_account(self):
        so = self.env['sale.order'].create({
            'partner_id': self.partner_customer_usd.id,
            'partner_invoice_id': self.partner_customer_usd.id,
            'partner_shipping_id': self.partner_customer_usd.id,
            'order_line': [(0, 0, {
                'name': self.product_order.name,
                'product_id': self.product_order.id,
                'product_uom_qty': 2,
                'product_uom': self.product_order.uom_id.id,
                'price_unit': self.product_order.list_price})],
            'picking_policy': 'direct',
            'fsm_location_id': self.location.id
        })
        # Confirming the sale order
        so.action_confirm()
        # A fsm order will be created

        for fsm_order in so.fsm_order_ids:

            # Assigning a worker and Scheduled Start Date , A Dayroute will be
            # created.
            fsm_order.write({'person_id': self.fsm_worker.id,
                             'scheduled_date_start': '2019-12-26 11:00:00'})
            # Creating invoice for sale order
            so.action_invoice_create()
            for invoice in so.invoice_ids:
                # Validating the invoice
                invoice.action_invoice_open()
                # Creating payment for invoice
                payment = self.env['account.payment'].create({
                    'payment_date': '2019-12-26',
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'amount': invoice.amount_total,
                    'currency_id': self.company.currency_id.id,
                    'journal_id': self.bank_journal.id,
                    'payment_method_id': self.payment_method_manual_in.id,
                    'invoice_ids': [(4, invoice.id)]

                })
                # Validating the payment
                payment.action_validate_invoice_payment()
                # A dayroute payment will be created.
                for dayroute_payment in\
                        fsm_order.dayroute_id.dayroute_payment_ids:
                    self.assertTrue(dayroute_payment)
                    self.assertEqual(dayroute_payment.amount_collected, 560.0)
                    dayroute_payment.amount_counted = 500
                    self.assertEqual(dayroute_payment.difference, 60.0)
                    dayroute_close_state = self.env['fsm.stage'].search(
                        ["&", ("stage_type", "=", "route"),
                         ("is_closed", "=", True)])
                    # Closing Day Route
                    fsm_order.dayroute_id.write(
                        {'stage_id': dayroute_close_state.id})
                    # A journal entry will be created.
                    self.assertTrue(dayroute_payment.move_id)
                    self.assertEqual(dayroute_payment.move_id.amount,
                                     dayroute_payment.difference)
