# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import fields
from odoo.tests.common import TransactionCase, Form
from odoo.exceptions import ValidationError


class FSMAccountCase(TransactionCase):

    def setUp(self):
        super(FSMAccountCase, self).setUp()
        self.WorkOrder = self.env['fsm.order']
        self.AccountInvoice = self.env['account.invoice']
        self.AccountInvoiceLine = self.env['account.invoice.line']
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
        # create expected FSM Location to compare to converted FSM Location
        self.test_location = self.env['fsm.location'].\
            create({
                'name': 'Test Location',
                'phone': '123',
                'email': 'tp@email.com',
                'partner_id': self.test_loc_partner.id,
                'owner_id': self.test_loc_partner.id,
                'customer_id': self.test_loc_partner.id,
                })
        self.test_person = self.env['fsm.person'].create({'name': 'Worker-1'})
        self.test_analytic = self.env.ref('analytic.analytic_administratif')

    def _create_workorder(self, bill_to, contractors, timesheets):
        # Create a new work order
        view_id = ('fieldservice.fsm_order_form')
        # Test that, if contractor_cost_ids is selected, the
        with Form(self.WorkOrder, view=view_id) as f:
            f.location_id = self.test_location
            f.bill_to = bill_to
            f.person_id = self.test_person
            for l in contractors:
                with f.contractor_cost_ids.new() as line:
                    line.product_id = l['product']
                    line.quantity = l['quantity']
                    line.price_unit = l['price_unit']
            for l in timesheets:
                with f.employee_timesheet_ids.new() as line:
                    line.account_id = f.location_id.analytic_account_id
                    line.employee_id = l['employee']
                    line.product_id = l['product']
                    line.unit_amount = l['unit_amount']
                    line.name = 'Test'
        order = f.save()
        order.person_ids += self.test_person
        return order

    def _process_order_to_invoices(self, order):
        # Change states
        order.action_confirm()
        order.action_request()
        order.action_assign()
        order.action_schedule()
        order.action_enroute()
        order.date_start = fields.Datetime.today()
        order.action_start()
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

    def test_fsm_order_bill_to_location(self):
        """Bill To Location,
        invoice created is based on this order's location's partner
        """
        # Setup required data
        self.test_location.analytic_account_id = self.test_analytic
        contractors = [{'product': self.env.ref('product.expense_hotel'),
                        'quantity': 2,
                        'price_unit': 200}, ]
        self.env.ref('hr.employee_qdp').timesheet_cost = 100.0
        timesheets = [{'employee': self.env.ref('hr.employee_qdp'),
                       'product': self.env.ref('product.expense_hotel'),
                       'unit_amount': 6},
                      {'employee': self.env.ref('hr.employee_qdp'),
                       'product': self.env.ref('product.expense_hotel'),
                       'unit_amount': 4}, ]
        order = self._create_workorder(bill_to='location',
                                       contractors=contractors,
                                       timesheets=timesheets)
        self.assertEqual(order.contractor_total, 400)
        self.assertEqual(order.employee_time_total, 10)  # Hrs
        self.assertEqual(order.total_cost, 1400)
        bill, invoice = self._process_order_to_invoices(order)
        self.assertEqual(bill.partner_id, order.person_id.partner_id)
        self.assertEqual(invoice.partner_id, order.location_id.customer_id)

    def test_fsm_order_bill_to_contact(self):
        """Bill To Contact,
        invoice created is based on this order's contact
        """
        # Setup required data
        self.test_location.analytic_account_id = self.test_analytic
        # Create a new work order with contract = 500 and timesheet = 300
        contractors = [{'product': self.env.ref('product.expense_hotel'),
                        'quantity': 2,
                        'price_unit': 100},
                       {'product': self.env.ref('product.expense_hotel'),
                        'quantity': 1,
                        'price_unit': 300}, ]
        self.env.ref('hr.employee_qdp').timesheet_cost = 20.0
        timesheets = [{'employee': self.env.ref('hr.employee_qdp'),
                       'product': self.env.ref('product.expense_hotel'),
                       'unit_amount': 10}, ]
        order = self._create_workorder(bill_to='contact',
                                       contractors=contractors,
                                       timesheets=timesheets)
        self.assertEqual(order.contractor_total, 500)
        self.assertEqual(order.employee_time_total, 10)  # Hrs
        self.assertEqual(order.total_cost, 700)
        bill, invoice = self._process_order_to_invoices(order)
        self.assertEqual(bill.partner_id, order.person_id.partner_id)
        self.assertEqual(invoice.partner_id, order.customer_id)

    def test_fsm_order_exception(self):
        """Create a new work order, error raised when
        - If person_is is not set, but user try to add new contractor_cost_ids
        - If analytic account is not set in location,
          and user create contractor_cost_ids (account.move.line)
        """
        # Create a new work order
        view_id = ('fieldservice.fsm_order_form')
        # Test if the person_id is not selected, error when add contractor line
        with Form(self.WorkOrder, view=view_id) as f:
            f.location_id = self.test_location
            f.bill_to = 'contact'
            with self.assertRaises(ValidationError) as e:
                with f.contractor_cost_ids.new() as line:
                    line.product_id = self.env.ref('product.expense_hotel')
            self.assertEqual(e.exception.name,
                             'Please set the field service worker.')
        order = f.save()
        f.person_id = self.test_person
        f.save()
        # Test analytic account is not set in location,
        # and user create account.invoice.line
        with self.assertRaises(ValidationError) as e:
            self.AccountInvoiceLine.create({
                'fsm_order_id': order.id,
                'product_id': self.env.ref('product.expense_hotel').id})
        self.assertEqual(e.exception.name,
                         "No analytic account set on the order's Location.")
        order.action_confirm()
        with self.assertRaises(ValidationError) as e:
            order.action_request()
        self.assertEqual(e.exception.name,
                         "Cannot move to Requested until "
                         "'Request Workers' is filled in")
        order.person_ids += self.test_person
        order.action_request()
        order.action_assign()
        order.action_schedule()
        order.action_enroute()
        order.date_start = fields.Datetime.today()
        order.action_start()
        order.date_end = fields.Datetime.today()
        order.resolution = 'Done something!'
        with self.assertRaises(ValidationError) as e:
            order.action_complete()
        self.assertEqual(e.exception.name,
                         "Cannot move to Complete until "
                         "'Employee Timesheets' is filled in")
