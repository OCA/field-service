# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent consulting Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import Command, fields
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("-at_install", "post_install")
class FSMAccountPaymentCase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company

        cls.env["account.chart.template"].try_loading(
            "generic_coa", company=cls.company, install_demo=False
        )
        cls.register_payments_model = cls.env["account.payment.register"]
        cls.payment_model = cls.env["account.payment"]

        cls.bank_journal = cls.env["account.journal"].search(
            [("company_id", "=", cls.company.id), ("type", "=", "bank")], limit=1
        )

        # create a Res Partner to be converted to FSM Location/Person
        cls.test_loc_partner = cls.env["res.partner"].create(
            {"name": "Test Loc Partner", "phone": "ABC", "email": "tlp@email.com"}
        )

        cls.inbound_payment_method_line = (
            cls.bank_journal.inbound_payment_method_line_ids[0]
        )

        cls.test_location = (
            cls.env["fsm.location"]
            .with_context(default_customer_id=cls.partner)
            .create(
                {
                    "name": "Test Location",
                    "phone": "123",
                    "email": "tp@email.com",
                    "partner_id": cls.test_loc_partner.id,
                    "owner_id": cls.test_loc_partner.id,
                }
            )
        )

        # Create a FSM order
        start = fields.Datetime.now().replace(microsecond=0, second=0)
        cls.test_order = cls.env["fsm.order"].create(
            {
                "location_id": cls.test_location.id,
                "date_start": start,
                "date_end": fields.Datetime.add(start, hours=2),
                "request_early": start,
            }
        )

        cls.test_order2 = cls.env["fsm.order"].create(
            {
                "location_id": cls.test_location.id,
                "date_start": start,
                "date_end": fields.Datetime.add(start, hours=2),
                "request_early": start,
            }
        )

        # Create an invoice
        cls.test_invoice = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "move_type": "out_invoice",
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": "Test",
                            "quantity": 1.00,
                            "price_unit": 100.00,
                            "tax_ids": [],
                        },
                    )
                ],
            }
        )

        cls.test_invoice.action_post()
        cls.test_order.invoice_lines = [Command.set(cls.test_invoice.line_ids.ids)]

    def test_fsm_account_payment(self):
        ctx = {
            "active_model": "account.move",
            "active_ids": self.test_invoice.ids,
        }
        register_payments = self.register_payments_model.with_context(**ctx).create(
            {
                "payment_date": fields.Date.today(),
                "journal_id": self.bank_journal.id,
                "payment_method_line_id": self.inbound_payment_method_line.id,
            }
        )
        payment = register_payments._create_payments()
        order = self.test_order
        payment._compute_fsm_order_ids()
        self.assertRecordValues(
            payment,
            [
                {"fsm_order_ids": [order.id]},
            ],
        )
        payment_copy = payment.copy()
        self.assertNotEqual(payment.fsm_order_ids, payment_copy.fsm_order_ids)
        order.payment_ids = [Command.set(payment.ids)]
        payment.action_view_fsm_orders()
        order.action_view_payments()
        self.assertAlmostEqual(payment.amount, 100)
        self.assertEqual(self.test_invoice.fsm_order_ids, payment.fsm_order_ids)
        res = self.env["fsm.order"].search([("payment_ids", "in", payment.id)])
        self.assertEqual(len(res), 1)
        self.test_invoice.fsm_order_ids = [Command.set([order.id, self.test_order2.id])]
        payment._compute_fsm_order_ids()
        payment.action_view_fsm_orders()
        payment2 = register_payments._create_payments()
        order.payment_ids = [Command.set([payment.id, payment2.id])]
        order.action_view_payments()
