# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.fieldservice_sale.tests.test_fsm_sale_order import TestFSMSaleOrder


class TestFSMSaleOrderNote(TestFSMSaleOrder):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_fsm_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_customer_usd.id,
                "pricelist_id": cls.pricelist_usd.id,
                "fsm_location_id": cls.test_location.id,
                "internal_note": "Test Internal Note",
            }
        )
        cls.env["sale.order.line"].create(
            {
                "name": cls.fsm_per_order_1.name,
                "product_id": cls.fsm_per_order_1.id,
                "product_uom_qty": 1,
                "product_uom": cls.fsm_per_order_1.uom_id.id,
                "price_unit": cls.fsm_per_order_1.list_price,
                "order_id": cls.sale_fsm_order.id,
                "tax_id": False,
            }
        )

    def test_sale_order(self):
        self.sale_fsm_order.action_confirm()
        self.assertEqual(
            self.sale_fsm_order.fsm_order_ids.resolution,
            self.sale_fsm_order.internal_note,
        )
        self.sale_fsm_order.write({"internal_note": "Test Updated Internal Note"})
        self.assertEqual(
            self.sale_fsm_order.fsm_order_ids.resolution,
            self.sale_fsm_order.internal_note,
        )
