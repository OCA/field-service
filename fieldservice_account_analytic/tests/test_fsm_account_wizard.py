# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class FSMAccountAnalyticCase(TransactionCase):
    def setUp(self):
        super(FSMAccountAnalyticCase, self).setUp()
        self.Wizard = self.env["fsm.wizard"]
        self.WorkOrder = self.env["fsm.order"]
        self.AccountInvoice = self.env["account.move"]
        self.AccountInvoiceLine = self.env["account.move.line"]
        # create a Res Partner
        self.test_partner = self.env["res.partner"].create(
            {"name": "Test Partner", "phone": "123", "email": "tp@email.com"}
        )
        # create a Res Partner to be converted to FSM Location/Person
        self.test_loc_partner = self.env["res.partner"].create(
            {"name": "Test Loc Partner", "phone": "ABC", "email": "tlp@email.com"}
        )
        self.test_loc_partner2 = self.env["res.partner"].create(
            {"name": "Test Loc Partner 2", "phone": "123", "email": "tlp@example.com"}
        )
        # create expected FSM Location to compare to converted FSM Location
        self.test_location = self.env["fsm.location"].create(
            {
                "name": "Test Location",
                "phone": "123",
                "email": "tp@email.com",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
                "customer_id": self.test_loc_partner.id,
            }
        )
        self.location = self.env["fsm.location"].create(
            {
                "name": "Location 1",
                "phone": "123",
                "email": "tp@email.com",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
                "customer_id": self.test_loc_partner.id,
            }
        )
        self.test_analytic_account = self.env["account.analytic.account"].create(
            {"name": "test_analytic_account"}
        )
        self.test_location2 = self.env["fsm.location"].create(
            {
                "name": "Test Location 2",
                "phone": "123",
                "email": "tp@email.com",
                "partner_id": self.test_loc_partner2.id,
                "owner_id": self.test_loc_partner2.id,
                "customer_id": self.test_loc_partner2.id,
                "fsm_parent_id": self.test_location.id,
                "analytic_account_id": self.test_analytic_account.id,
            }
        )
        self.default_account_revenue = self.env["account.account"].search(
            [
                ("company_id", "=", self.env.user.company_id.id),
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_revenue").id,
                ),
            ],
            limit=1,
        )
        self.move_line = self.env["account.move.line"]
        self.analytic_line = self.env["account.analytic.line"]
        self.product1 = self.env["product.product"].create(
            {
                "name": "Product A",
                "detailed_type": "consu",
            }
        )

    def test_convert_contact_to_fsm_loc(self):
        """
        Test converting a contact to a location to make sure the customer_id
        and owner_id get set correctly
        :return:
        """
        self.Wizard._prepare_fsm_location(self.test_partner)
        # check if there is a new FSM Location with the same name
        self.wiz_location = self.env["fsm.location"].search(
            [("name", "=", self.test_loc_partner2.name)]
        )

        # check if location is created successfully and fields copied over
        self.assertEqual(self.test_loc_partner2, self.wiz_location.customer_id)
        self.assertEqual(self.test_loc_partner2, self.wiz_location.owner_id)

    def test_fsm_orders_1(self):
        """Test creating new workorders, and test following functions."""
        # Create an Orders
        hours_diff = 100
        date_start = fields.Datetime.today()
        order = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "date_start": date_start,
                "customer_id": self.test_partner.id,
                "date_end": date_start + timedelta(hours=hours_diff),
                "request_early": fields.Datetime.today(),
            }
        )
        order2 = self.env["fsm.order"].create(
            {
                "location_id": self.test_location2.id,
                "date_start": fields.datetime.today(),
                "date_end": fields.datetime.today() + timedelta(hours=2),
                "request_early": fields.datetime.today(),
            }
        )
        order4 = self.env["fsm.order"].create(
            {
                "location_id": self.location.id,
                "date_start": fields.datetime.today(),
                "date_end": fields.datetime.today() + timedelta(hours=2),
                "request_early": fields.datetime.today(),
            }
        )
        order._compute_total_cost()
        order4._compute_total_cost()
        self.env.user.company_id.fsm_filter_location_by_contact = True
        self.test_location2.get_default_customer()
        general_journal = self.env["account.journal"].search(
            [
                ("company_id", "=", self.env.user.company_id.id),
                ("type", "=", "general"),
            ],
            limit=1,
        )
        general_move1 = self.env["account.move"].create(
            {
                "name": "general1",
                "journal_id": general_journal.id,
            }
        )
        self.move_line.create(
            [
                {
                    "account_id": self.default_account_revenue.id,
                    "analytic_account_id": self.test_analytic_account.id,
                    "fsm_order_ids": [(6, 0, order2.ids)],
                    "move_id": general_move1.id,
                }
            ]
        )
        with self.assertRaises(ValidationError):
            self.move_line.create(
                {
                    "account_id": self.default_account_revenue.id,
                    "analytic_account_id": self.test_analytic_account.id,
                    "fsm_order_ids": [(6, 0, order.ids)],
                }
            )

        self.analytic_line.create(
            {
                "fsm_order_id": order2.id,
                "name": "Test01",
                "product_id": self.product1.id,
            }
        )
        self.analytic_line.onchange_product_id()
        with self.assertRaises(ValidationError):
            self.analytic_line.create(
                {
                    "fsm_order_id": order.id,
                    "name": "Test01",
                }
            )
        order._onchange_customer_id_location()
        self.test_location2._onchange_fsm_parent_id_account()
        self.env["res.partner"].with_context(location_id=self.test_location2.id).search(
            []
        )
        self.env["fsm.location"].with_context(customer_id=self.test_partner.id).search(
            []
        )
