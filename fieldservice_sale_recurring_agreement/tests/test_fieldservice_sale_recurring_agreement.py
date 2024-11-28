# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author: Italo Lopes <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestFieldserviceSaleRecurringAgreement(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order_model = cls.env["sale.order"].with_context(tracking_disable=True)
        cls.sale_order_line_model = cls.env["sale.order.line"]
        cls.fsm_recurring_model = cls.env["fsm.recurring"]
        cls.agreement_model = cls.env["agreement"]
        cls.product_model = cls.env["product.product"]
        cls.partner_model = cls.env["res.partner"]

        cls.test_location = cls.env.ref("fieldservice.test_location")
        cls.pricelist = cls.env["product.pricelist"].search([], limit=1)

        cls.partner = cls.partner_model.create({"name": "Test Partner"})
        cls.agreement = cls.agreement_model.create(
            {
                "name": "Test Agreement",
                "code": "TestAgreement",
                "start_date": fields.Date.today(),
                "end_date": fields.Date.today(),
            }
        )
        cls.product = cls.product_model.create(
            {
                "name": "Test Product",
                "type": "service",
                "field_service_tracking": "recurring",
                "fsm_recurring_template_id": cls.env.ref(
                    "fieldservice_recurring.recur_template_weekdays"
                ).id,
            }
        )
        cls.sale_order = cls.sale_order_model.create(
            {
                "partner_id": cls.partner.id,
                "fsm_location_id": cls.test_location.id,
                "pricelist_id": cls.pricelist.id,
                "agreement_id": cls.agreement.id,
            }
        )
        cls.sale_line_recurring = cls.env["sale.order.line"].create(
            {
                "name": cls.product.name,
                "product_id": cls.product.id,
                "product_uom_qty": 1,
                "product_uom": cls.product.uom_id.id,
                "price_unit": cls.product.list_price,
                "order_id": cls.sale_order.id,
                "tax_id": False,
            }
        )

    def test_01_sale_order_with_agreement_propagation(self):
        self.sale_order.action_confirm()
        fsm_recurring = self.fsm_recurring_model.search(
            [("sale_line_id", "=", self.sale_line_recurring.id)]
        )
        prepare_recurring_values = (
            self.sale_line_recurring._field_create_fsm_recurring_prepare_values()
        )
        self.assertEqual(prepare_recurring_values["agreement_id"], self.agreement.id)

        self.assertTrue(fsm_recurring)
        self.assertEqual(fsm_recurring.agreement_id, self.agreement)
        order_values = fsm_recurring._prepare_order_values()
        self.assertEqual(order_values["agreement_id"], self.agreement.id)

        fsm_recurring.action_start()
        for order in fsm_recurring.fsm_order_ids:
            self.assertEqual(order.agreement_id, self.agreement)
