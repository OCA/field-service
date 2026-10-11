# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class FSMAccountAnalyticCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.Wizard = cls.env["fsm.wizard"]
        cls.WorkOrder = cls.env["fsm.order"]
        cls.AccountMoveLine = cls.env["account.move.line"]
        cls.AnalyticLine = cls.env["account.analytic.line"]
        # create a Res Partner
        cls.test_partner = cls.env["res.partner"].create(
            {"name": "Test Partner", "phone": "123", "email": "tp@email.com"}
        )
        # create Res Partners to be linked to FSM Locations
        cls.test_loc_partner = cls.env["res.partner"].create(
            {"name": "Test Loc Partner", "phone": "ABC", "email": "tlp@email.com"}
        )
        cls.test_loc_partner2 = cls.env["res.partner"].create(
            {"name": "Test Loc Partner 2", "phone": "123", "email": "tlp@example.com"}
        )
        # location without analytic account nor explicit customer
        cls.test_location = cls.env["fsm.location"].create(
            {
                "name": "Test Location",
                "phone": "123",
                "email": "tp@email.com",
                "partner_id": cls.test_loc_partner.id,
                "owner_id": cls.test_loc_partner.id,
            }
        )
        cls.location = cls.env["fsm.location"].create(
            {
                "name": "Location 1",
                "phone": "123",
                "email": "tp@email.com",
                "partner_id": cls.test_loc_partner.id,
                "owner_id": cls.test_loc_partner.id,
            }
        )
        cls.test_analytic_plan = cls.env["account.analytic.plan"].create(
            {"name": "test_analytic_plan"}
        )
        cls.test_analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "test_analytic_account",
                "plan_id": cls.test_analytic_plan.id,
            }
        )
        # child location with an analytic account, customer computed from parent
        cls.test_location2 = cls.env["fsm.location"].create(
            {
                "name": "Test Location 2",
                "phone": "123",
                "email": "tp@email.com",
                "partner_id": cls.test_loc_partner2.id,
                "owner_id": cls.test_loc_partner2.id,
                "fsm_parent_id": cls.test_location.id,
                "analytic_account_id": cls.test_analytic_account.id,
            }
        )
        cls.default_account_revenue = cls.env["account.account"].search(
            [("account_type", "=", "income")],
            limit=1,
        )
        cls.general_journal = cls.env["account.journal"].search(
            [
                ("company_id", "=", cls.env.company.id),
                ("type", "=", "general"),
            ],
            limit=1,
        )
        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "consu",
            }
        )

    @classmethod
    def _create_order(cls, location):
        date_start = fields.Datetime.today()
        return cls.WorkOrder.create(
            {
                "location_id": location.id,
                "date_start": date_start,
                "date_end": date_start + timedelta(hours=2),
                "request_early": date_start,
            }
        )

    def test_customer_id_computation(self):
        """The billed customer defaults to the owner, and to the parent
        location's customer for child locations."""
        self.assertEqual(self.test_location.customer_id, self.test_loc_partner)
        # child location: parent's customer wins over its own owner
        self.assertEqual(self.test_location2.customer_id, self.test_loc_partner)
        # an explicit value is kept when there is no parent customer
        location = self.env["fsm.location"].create(
            {
                "name": "Location Explicit",
                "partner_id": self.test_loc_partner2.id,
                "owner_id": self.test_loc_partner2.id,
                "customer_id": self.test_partner.id,
            }
        )
        self.assertEqual(location.customer_id, self.test_partner)

    def test_convert_contact_to_fsm_loc(self):
        """Converting a contact to a location must set the customer_id
        and owner_id correctly."""
        self.Wizard.action_convert_location(self.test_partner)
        wiz_location = self.env["fsm.location"].search(
            [("partner_id", "=", self.test_partner.id)]
        )
        self.assertEqual(len(wiz_location), 1)
        self.assertEqual(wiz_location.customer_id, self.test_partner)
        self.assertEqual(wiz_location.owner_id, self.test_partner)

    def test_move_line_analytic_distribution(self):
        """Move lines linked to FSM orders get the analytic account of the
        order's location in their analytic distribution."""
        order = self._create_order(self.test_location2)
        move = self.env["account.move"].create({"journal_id": self.general_journal.id})
        line = self.AccountMoveLine.create(
            {
                "account_id": self.default_account_revenue.id,
                "fsm_order_ids": [fields.Command.set(order.ids)],
                "move_id": move.id,
            }
        )
        self.assertEqual(
            line.analytic_distribution,
            {str(self.test_analytic_account.id): 100},
        )

    def test_move_line_missing_analytic_account(self):
        """Linking a move line to an order whose location has no analytic
        account raises an error."""
        order = self._create_order(self.test_location)
        move = self.env["account.move"].create({"journal_id": self.general_journal.id})
        with self.assertRaises(ValidationError):
            self.AccountMoveLine.create(
                {
                    "account_id": self.default_account_revenue.id,
                    "fsm_order_ids": [fields.Command.set(order.ids)],
                    "move_id": move.id,
                }
            )

    def test_analytic_line(self):
        """Analytic lines linked to FSM orders get the analytic account of
        the order's location."""
        order = self._create_order(self.test_location2)
        analytic_line = self.AnalyticLine.create(
            {
                "fsm_order_id": order.id,
                "name": "Test01",
                "product_id": self.product1.id,
            }
        )
        self.assertEqual(analytic_line.account_id, self.test_analytic_account)
        order2 = self._create_order(self.test_location)
        with self.assertRaises(ValidationError):
            self.AnalyticLine.create(
                {
                    "fsm_order_id": order2.id,
                    "name": "Test02",
                }
            )

    def test_order_customer(self):
        """The order's customer is taken from the location when not set,
        and the location follows the customer's service location."""
        order = self._create_order(self.test_location2)
        self.assertFalse(order.customer_id)
        order.write({"description": "Test description"})
        self.assertEqual(order.customer_id, self.test_location2.customer_id)
        order._compute_total_cost()
        self.assertEqual(order.total_cost, 0.0)
        # onchange: the location follows the customer's service location
        self.test_partner.service_location_id = self.test_location2
        order.customer_id = self.test_partner
        order._onchange_customer_id_location()
        self.assertEqual(order.location_id, self.test_location2)

    def test_filtered_searches(self):
        """Contextual filters on partners and locations."""
        self.env.company.fsm_filter_location_by_contact = True
        self.test_partner.service_location_id = self.test_location2
        partners = (
            self.env["res.partner"]
            .with_context(location_id=self.test_location2.id)
            .search([("id", "in", (self.test_partner | self.test_loc_partner).ids)])
        )
        self.assertEqual(partners, self.test_partner)
        locations = (
            self.env["fsm.location"]
            .with_context(customer_id=self.test_loc_partner.id)
            .search([])
        )
        self.assertIn(self.test_location, locations)
        self.assertNotIn(self.test_location2, locations)
