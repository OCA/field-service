# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase


class FSMAccountCase(TransactionCase):
    def setUp(self):
        super(FSMAccountCase, self).setUp()
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
            }
        )
        self.test_order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "date_start": datetime.today(),
                "date_end": datetime.today() + timedelta(hours=2),
                "request_early": datetime.today(),
            }
        )
        self.test_order2 = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "date_start": datetime.today(),
                "date_end": datetime.today() + timedelta(hours=2),
                "request_early": datetime.today(),
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
        self.test_invoice = self.env["account.move"].create(
            {
                "partner_id": self.test_partner.id,
                "move_type": "out_invoice",
                "invoice_date": datetime.today().date(),
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test",
                            "quantity": 1.00,
                            "price_unit": 100.00,
                        },
                    )
                ],
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "line_debit",
                            "account_id": self.default_account_revenue.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "line_credit",
                            "account_id": self.default_account_revenue.id,
                        },
                    ),
                ],
            }
        )
        self.test_invoice2 = self.env["account.move"].create(
            {
                "partner_id": self.test_partner.id,
                "move_type": "out_invoice",
                "invoice_date": datetime.today().date(),
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test1",
                            "quantity": 1.00,
                            "price_unit": 100.00,
                        },
                    )
                ],
            }
        )

    def test_fsm_account_move(self):
        self.test_order.invoice_lines = [(6, 0, self.test_invoice.line_ids.ids)]
        self.test_invoice.action_view_fsm_orders()
        self.test_order2.invoice_lines = [(6, 0, self.test_invoice.line_ids.ids)]
        self.test_invoice._compute_fsm_order_ids()
        self.test_invoice.action_view_fsm_orders()
        self.test_order._compute_get_invoiced()
        self.test_order.action_view_invoices()
        self.test_order2.invoice_ids = [
            (6, 0, [self.test_invoice.id, self.test_invoice2.id])
        ]
        self.test_order2.action_view_invoices()
