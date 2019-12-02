# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields
from odoo.addons.fieldservice_account.tests.test_fsm_account import (
    FSMAccountCase
)
from odoo.exceptions import ValidationError


class FSMAccountCase(FSMAccountCase):

    def setUp(self):
        super(FSMAccountCase, self).setUp()
        self.test_person = self.env['fsm.person'].create({'name': 'Worker-1'})
        self.test_analytic = self.env.ref('analytic.analytic_administratif')
        self.account_id = self.env['account.account'].create({
            'code': 'NC1110',
            'name': 'Test Payable Account',
            'user_type_id':
                self.env.ref('account.data_account_type_payable').id,
            'reconcile': True
        })

    def _create_workorder(self, bill_to, contractors, timesheets):
        # Create a new work order
        contractors = self.env['account.invoice.line'].create(contractors)
        timesheets = self.env['account.analytic.line'].create(timesheets)

        order = self.env['fsm.order'].\
            create({
                'location_id': self.test_location.id,
                'bill_to': bill_to,
                'person_id': self.test_person.id,
                'contractor_cost_ids': [(6, 0, contractors.ids)],
                'employee_timesheet_ids': [(6, 0, timesheets.ids)]
            })
        order.person_ids += self.test_person
        return order

    def _process_order_to_invoices(self, order):
        # Change states
        order.date_start = fields.Datetime.today()
        order.date_end = fields.Datetime.today()
        order.resolution = 'Done something!'
        order.action_complete()
        self.assertEqual(order.account_stage, 'review')
        # Create vendor bill
        # Vendor bill created from order's contractor
        if not order.person_id.partner_id.supplier:
            with self.assertRaises(ValidationError) as e:
                order.account_confirm()
            self.assertEqual(
                e.exception.name,
                "The worker assigned to this order is not a supplier")
            order.person_id.partner_id.supplier = True
        order.account_confirm()
        self.assertEqual(order.account_stage, 'confirmed')
        bill = self.AccountInvoice.search([('type', '=', 'in_invoice'),
                                           ('fsm_order_id', '=', order.id)])
        self.assertEqual(len(bill), 1)
        self.assertEqual(len(order.contractor_cost_ids),
                         len(bill.invoice_line_ids))
        # Customer invoice created from order's contractor and timehsheet
        if order.bill_to == 'contact' and not order.customer_id:
            with self.assertRaises(ValidationError):
                order.account_create_invoice()
            order.customer_id = self.test_loc_partner  # Assign some partner
        order.account_create_invoice()
        self.assertEqual(order.account_stage, 'invoiced')
        invoice = self.AccountInvoice.search([('type', '=', 'out_invoice'),
                                              ('fsm_order_id', '=', order.id)])
        self.assertEqual(len(invoice), 1)
        self.assertEqual(
            len(order.contractor_cost_ids) + len(order.employee_timesheet_ids),
            len(invoice.invoice_line_ids))
        return (bill, invoice)

    def test_fsm_order_exception(self):
        """Create a new work order, error raised when
        - If person_is is not set, but user try to add new contractor_cost_ids
        - If analytic account is not set in location,
          and user create contractor_cost_ids (account.move.line)
        """
        # Test if the person_id is not selected, error when add contractor line
        # Setup required data
        self.test_location.analytic_account_id = self.test_analytic
        # Create a new work order with contract = 500 and timesheet = 300
        self.env.ref('hr.employee_qdp').timesheet_cost = 20.0
        order = self.env['fsm.order'].\
            create({
                'location_id': self.test_location.id,
                'person_id': self.test_person.id,
            })
        order.person_id = self.test_person

        order.person_ids += self.test_person
        order.date_start = fields.Datetime.today()
        order.date_end = fields.Datetime.today()
        order.resolution = 'Done something!'
        with self.assertRaises(ValidationError) as e:
            order.action_complete()
        self.assertEqual(e.exception.name,
                         "Cannot move to Complete until "
                         "'Employee Timesheets' is filled in")

    def test_fsm_order_bill_to_location(self):
        """Bill To Location,
        invoice created is based on this order's location's partner
        """
        # Setup required data
        self.test_location.analytic_account_id = self.test_analytic
        contractors = [{'name': 'contractor_line_1',
                        'product_id': self.env.ref('product.expense_hotel').id,
                        'account_id': self.account_id.id,
                        'quantity': 2,
                        'price_unit': 200}, ]
        self.env.ref('hr.employee_qdp').timesheet_cost = 100
        timesheets = [{'name': 'timesheet_line_1',
                       'employee_id': self.env.ref('hr.employee_qdp').id,
                       'account_id': self.test_analytic.id,
                       'product_id': self.env.ref('product.expense_hotel').id,
                       'unit_amount': 6},
                      {'name': 'timesheet_line_2',
                       'employee_id': self.env.ref('hr.employee_qdp').id,
                       'account_id': self.test_analytic.id,
                       'product_id': self.env.ref('product.expense_hotel').id,
                       'unit_amount': 4}, ]
        order = self._create_workorder(bill_to='location',
                                       contractors=contractors,
                                       timesheets=timesheets)
        order._compute_contractor_cost()
        order._compute_employee_hours()
        order._compute_total_cost()
        self.assertEqual(order.contractor_total, 400)
        self.assertEqual(order.employee_time_total, 10)  # Hrs
        self.assertEqual(order.total_cost, 1400)
        # Testing not working "Need to Configure Chart of Accounts"
        # bill, invoice = self._process_order_to_invoices(order)
        # self.assertEqual(bill.partner_id, order.person_id.partner_id)
        # self.assertEqual(invoice.partner_id, order.location_id.customer_id)

    def test_fsm_order_bill_to_contact(self):
        """Bill To Contact,
        invoice created is based on this order's contact
        """
        # Setup required data
        self.test_location.analytic_account_id = self.test_analytic
        # Create a new work order with contract = 500 and timesheet = 300
        contractors = [{'name': 'contractor_line_2',
                        'product_id': self.env.ref('product.expense_hotel').id,
                        'account_id': self.account_id.id,
                        'quantity': 2,
                        'price_unit': 100},
                       {'name': 'contractor_line_3',
                        'product_id': self.env.ref('product.expense_hotel').id,
                        'account_id': self.account_id.id,
                        'quantity': 1,
                        'price_unit': 300}, ]
        self.env.ref('hr.employee_qdp').timesheet_cost = 20.0
        timesheets = [{'name': 'timesheet_line_3',
                       'employee_id': self.env.ref('hr.employee_qdp').id,
                       'account_id': self.test_analytic.id,
                       'product_id': self.env.ref('product.expense_hotel').id,
                       'unit_amount': 10}, ]
        order = self._create_workorder(bill_to='contact',
                                       contractors=contractors,
                                       timesheets=timesheets)
        order._compute_contractor_cost()
        order._compute_employee_hours()
        order._compute_total_cost()
        self.assertEqual(order.contractor_total, 500)
        self.assertEqual(order.employee_time_total, 10)  # Hrs
        self.assertEqual(order.total_cost, 700)
        # Testing not working "Need to Configure Chart of Accounts"
        # bill, invoice = self._process_order_to_invoices(order)
        # self.assertEqual(bill.partner_id, order.person_id.partner_id)
        # self.assertEqual(invoice.partner_id, order.customer_id)
