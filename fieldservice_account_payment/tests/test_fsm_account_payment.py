# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent consulting Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import Command, fields
from odoo.tests import tagged

from odoo.addons.fieldservice_account.tests.test_fsm_account import FSMAccountCase


@tagged("-at_install", "post_install")
class FSMAccountPaymentCase(FSMAccountCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.register_payments_model = cls.env["account.payment.register"].with_context(
            active_model="account.move"
        )
        cls.payment_model = cls.env["account.payment"]

        cls.company = cls.env.user.company_id

        cls.bank_journal = (
            cls.env["account.journal"]
            .search(
                [("company_id", "=", cls.company.id), ("type", "=", "bank")], limit=1
            )
            .ensure_one()
        )
        cls.inbound_payment_method_line = (
            cls.bank_journal.inbound_payment_method_line_ids[0]
        )

        cls.test_invoice.invoice_line_ids.update({"tax_ids": [Command.clear()]})
        cls.test_invoice.action_post()

    def test_fsm_account_payment(self):
        ctx = {
            "active_model": "account.move",
            "active_id": self.test_invoice.id,
            "active_ids": self.test_invoice.ids,
        }
        register_payments = self.register_payments_model.with_context(**ctx).create(
            {
                "payment_date": fields.Date.today(),
                "journal_id": self.bank_journal.id,
                "payment_method_line_id": self.inbound_payment_method_line.id,
            }
        )
        order = self.test_order
        register_payment_action = register_payments.action_create_payments()
        payment = self.payment_model.browse(register_payment_action.get("res_id"))
        test_order = self.test_order.id
        payment.fsm_order_ids = [Command.set(self.test_order.ids)]
        payment_copy = payment.copy()
        self.assertNotEqual(payment.fsm_order_ids, payment_copy.fsm_order_ids)
        self.test_invoice.fsm_order_ids = [Command.set(self.test_order.ids)]
        order.payment_ids = [Command.set(payment.ids)]
        payment.action_view_fsm_orders()
        order.action_view_payments()
        self.assertAlmostEqual(payment.amount, 100)
        self.assertEqual(payment.state, "posted")
        self.assertEqual(self.test_invoice.state, "posted")
        self.assertEqual(self.test_invoice.fsm_order_ids, payment.fsm_order_ids)
        res = self.env["fsm.order"].search([("payment_ids", "in", payment.id)])
        self.assertEqual(len(res), 1)
        payment.fsm_order_ids = [Command.set([test_order, self.test_order2.id])]
        payment.action_view_fsm_orders()
        register_payment_action2 = register_payments.action_create_payments()
        payment2 = self.payment_model.browse(register_payment_action2.get("res_id"))
        order.payment_ids = [Command.set([payment.id, payment2.id])]
        order.action_view_payments()
