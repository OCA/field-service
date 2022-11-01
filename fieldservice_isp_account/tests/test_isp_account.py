# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class FSMISPAccountCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(FSMISPAccountCase, cls).setUpClass()
        cls.AccountMoveLine = cls.env["account.move.line"]
        cls.test_person = cls.env["fsm.person"].create({"name": "Worker-1"})
        cls.test_person2 = cls.env["fsm.person"].create(
            {"name": "Worker-1", "supplier_rank": 1}
        )
        cls.test_analytic = cls.env.ref("analytic.analytic_administratif")
        cls.account_id = cls.env["account.account"].create(
            {
                "code": "NC1110",
                "name": "Test Payable Account",
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
                "reconcile": True,
            }
        )
        # create a Res Partner to be converted to FSM Location/Person
        cls.test_loc_partner = cls.env["res.partner"].create(
            {"name": "Test Loc Partner", "phone": "ABC", "email": "tlp@email.com"}
        )
        # create expected FSM Location to compare to converted FSM Location
        cls.test_location = cls.env["fsm.location"].create(
            {
                "name": "Test Location",
                "phone": "123",
                "email": "tp@email.com",
                "partner_id": cls.test_loc_partner.id,
                "owner_id": cls.test_loc_partner.id,
                "customer_id": cls.test_loc_partner.id,
            }
        )

    def _create_workorder(self, bill_to, contractors, timesheets):
        # Create a new work order
        timesheets = self.env["account.analytic.line"].create(timesheets)

        order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "bill_to": bill_to,
                "person_id": self.test_person.id,
                "employee_timesheet_ids": [(6, 0, timesheets.ids)],
            }
        )
        order2 = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "bill_to": bill_to,
                "person_id": self.test_person.id,
            }
        )
        order3 = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "bill_to": bill_to,
                "person_id": self.test_person2.id,
            }
        )
        order._compute_employee()
        self.test_person._compute_vendor_bills()
        self.test_person.action_view_bills()
        with self.assertRaises(ValidationError):
            order2.action_complete()
        with self.assertRaises(ValidationError):
            order3.action_complete()
        for contractor in contractors:
            contractor.update({"fsm_order_id": order.id})
        contractors = self.env["fsm.order.cost"].create(contractors)
        contractors.onchange_product_id()
        order.write({"contractor_cost_ids": [(6, 0, contractors.ids)]})
        order.person_ids += self.test_person
        order.account_no_invoice()
        return order

    def _process_order_to_invoices(self, order):
        # Change states
        order.date_start = fields.Datetime.today()
        order.date_end = fields.Datetime.today()
        order.resolution = "Done something!"
        order.action_complete()
        order3 = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "bill_to": "contact",
                "person_id": self.test_person2.id,
                "customer_id": self.test_loc_partner.id,
            }
        )
        self.assertEqual(order.account_stage, "review")
        # Create vendor bill
        # Vendor bill created from order's contractor
        if not order.person_id.partner_id.supplier_rank:
            with self.assertRaises(ValidationError):
                order.account_confirm()
            order.person_id.partner_id.supplier_rank = True
        order.account_confirm()
        self.assertEqual(order.account_stage, "confirmed")
        bill = self.AccountMoveLine.search(
            [("fsm_order_ids", "in", order.id)]
        ).move_id.filtered(lambda i: i.move_type == "in_invoice")
        self.test_person.action_view_bills()
        self.assertEqual(len(bill), 1)
        self.assertEqual(len(order.contractor_cost_ids), len(bill.invoice_line_ids))
        order3.account_create_invoice()
        order.account_create_invoice()
        self.assertEqual(order.account_stage, "invoiced")
        invoice = self.AccountMoveLine.search(
            [("fsm_order_ids", "in", order.id)]
        ).move_id.filtered(lambda i: i.move_type == "out_invoice")
        self.assertEqual(len(invoice), 1)
        self.assertEqual(
            len(order.contractor_cost_ids) + len(order.employee_timesheet_ids),
            len(invoice.invoice_line_ids),
        )
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
        self.env.ref("hr.employee_qdp").timesheet_cost = 20.0
        order = self.env["fsm.order"].create(
            {"location_id": self.test_location.id, "person_id": self.test_person.id}
        )
        order.person_id = self.test_person

        order.person_ids += self.test_person
        order.date_start = fields.Datetime.today()
        order.date_end = fields.Datetime.today()
        order.resolution = "Done something!"
        with self.assertRaises(ValidationError):
            order.action_complete()

    def test_fsm_order_bill_to_location(self):
        """Bill To Location,
        invoice created is based on this order's location's partner
        """
        # Setup required data
        self.test_location.analytic_account_id = self.test_analytic
        contractors = [
            {
                "product_id": self.env.ref("product.expense_hotel").id,
                "quantity": 2,
                "price_unit": 200,
            },
        ]
        self.env.ref("hr.employee_qdp").timesheet_cost = 100
        timesheets = [
            {
                "name": "timesheet_line_1",
                "employee_id": self.env.ref("hr.employee_qdp").id,
                "account_id": self.test_analytic.id,
                "product_id": self.env.ref("product.expense_hotel").id,
                "unit_amount": 6,
            },
            {
                "name": "timesheet_line_2",
                "employee_id": self.env.ref("hr.employee_qdp").id,
                "account_id": self.test_analytic.id,
                "product_id": self.env.ref("product.expense_hotel").id,
                "unit_amount": 4,
            },
        ]
        order = self._create_workorder(
            bill_to="location", contractors=contractors, timesheets=timesheets
        )
        order._compute_contractor_cost()
        order._compute_employee_hours()
        order._compute_total_cost()
        self.assertEqual(order.contractor_total, 800.0)
        self.assertEqual(order.employee_time_total, 10)  # Hrs
        self.assertEqual(order.total_cost, 1800.0)
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
        contractors = [
            {
                "product_id": self.env.ref("product.expense_hotel").id,
                "quantity": 2,
                "price_unit": 100,
            },
            {
                "product_id": self.env.ref("product.expense_hotel").id,
                "quantity": 1,
                "price_unit": 300,
            },
        ]
        self.env.ref("hr.employee_qdp").timesheet_cost = 20.0
        timesheets = [
            {
                "name": "timesheet_line_3",
                "employee_id": self.env.ref("hr.employee_qdp").id,
                "account_id": self.test_analytic.id,
                "product_id": self.env.ref("product.expense_hotel").id,
                "unit_amount": 10,
            },
        ]
        order = self._create_workorder(
            bill_to="contact", contractors=contractors, timesheets=timesheets
        )
        order._compute_contractor_cost()
        order._compute_employee_hours()
        order._compute_total_cost()
        self.assertEqual(order.contractor_total, 1200.0)
        self.assertEqual(order.employee_time_total, 10)  # Hrs
        self.assertEqual(order.total_cost, 1400.0)
