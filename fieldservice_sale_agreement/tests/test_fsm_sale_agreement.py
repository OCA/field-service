# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
from odoo.addons.sale.tests.common import TestSaleCommonBase


class TestFieldServiceSaleAgreement(TestSaleCommonBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.fsm_template = cls.env["fsm.template"].create(
            {
                "name": "Test FSM Template",
                "instructions": "Test Notes",
                "duration": 2,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "FSM Product",
                "type": "service",
                "invoice_policy": "delivery",
                "field_service_tracking": "line",
                "fsm_order_template_id": cls.fsm_template.id,
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.ref("base.main_partner").id,
                "agreement_id": cls.env.ref("agreement.market1").id,
                "fsm_location_id": cls.env.ref("fieldservice.test_location").id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )

    def test_propagate_agreement_id(self):
        self.order.action_confirm()
        self.assertTrue(
            self.order.fsm_order_ids, "The FSM Order should've been created"
        )
        self.assertEqual(
            self.order.fsm_order_ids.agreement_id,
            self.order.agreement_id,
            "The FSM Order should have the same agreement as the Sale Order",
        )
