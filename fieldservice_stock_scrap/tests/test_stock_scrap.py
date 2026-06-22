# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime

from odoo import exceptions
from odoo.tests.common import Form, TransactionCase


class SomethingCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.StockRequest = cls.env["stock.request"]
        cls.product_01 = cls.env.ref("product.product_delivery_01")
        cls.product_02 = cls.env.ref("product.product_delivery_02")
        cls.product_03 = cls.env.ref("product.product_order_01")
        cls.fsm_order_id = cls.env["fsm.order"].create(
            {"location_id": cls.env.ref("fieldservice.test_location").id}
        )
        cls.warehouse_id = cls.env.ref("stock.warehouse0")
        cls.stock_request1 = cls.StockRequest.create(
            {
                "product_id": cls.product_01.id,
                "warehouse_id": cls.warehouse_id.id,
                "product_uom_qty": 5.0,
                "product_uom_id": cls.product_01.uom_id.id,
                "fsm_order_id": cls.fsm_order_id.id,
                "expected_date": datetime.datetime.now(),
                "location_id": cls.warehouse_id.lot_stock_id.id,
                "direction": "inbound",
                "picking_policy": "direct",
            }
        )
        cls.stock_request2 = cls.StockRequest.create(
            {
                "product_id": cls.product_02.id,
                "product_uom_qty": 5.0,
                "warehouse_id": cls.env.ref("stock.warehouse0").id,
                "product_uom_id": cls.product_02.uom_id.id,
                "expected_date": datetime.datetime.now(),
                "fsm_order_id": cls.fsm_order_id.id,
                "location_id": cls.warehouse_id.lot_stock_id.id,
                "direction": "inbound",
                "picking_policy": "direct",
            },
        )
        cls.stock_request3 = cls.StockRequest.create(
            {
                "product_id": cls.product_03.id,
                "product_uom_qty": 5.0,
                "product_uom_id": cls.product_03.uom_id.id,
                "fsm_order_id": cls.fsm_order_id.id,
                "expected_date": datetime.datetime.now(),
                "location_id": cls.warehouse_id.lot_stock_id.id,
                "direction": "outbound",
                "picking_policy": "direct",
            },
        )
        wizard_form = Form(
            cls.env["scrap.stock.wizard"].with_context(fsm_order_id=cls.fsm_order_id.id)
        )
        cls.wizard = wizard_form.save()

    def test_stock_scrap(self):
        self.assertEqual(self.wizard.scrap_stock_entries[0].product_id, self.product_01)
        self.assertEqual(self.wizard.scrap_stock_entries[1].product_id, self.product_02)
        self.assertEqual(len(self.wizard.scrap_stock_entries), 2)
        self.wizard.scrap_stock_entries[1].scrap_qty = 4.0
        with self.assertRaises(exceptions.ValidationError):
            self.wizard.scrap_stock_entries[0].scrap_qty = 6.0
        self.wizard.scrap_stock_entries[0].scrap_qty = 5.0
        self.wizard.scrap_stock_entries[1].scrap_qty = 4.0
        self.wizard.action_scrap()
        # Initial Stock Request 3, now 2
        self.assertEqual(
            len(
                self.wizard.scrap_stock_entries.stock_request_id.fsm_order_id.stock_request_ids
            ),
            2,
        )
        # 4 move_ids, 2 for internal transfer and 2 for scraps
        self.assertEqual(
            len(
                self.wizard.scrap_stock_entries.stock_request_id.fsm_order_id.scrap_ids.move_ids
            ),
            4,
        )
        # 2 for scraps
        self.assertEqual(
            self.wizard.scrap_stock_entries.stock_request_id.fsm_order_id.scrap_count, 2
        )
        # Remove 1 stock request directly with wizard
        self.wizard.scrap_stock_entries.unlink()
        self.wizard.action_scrap()
        self.assertFalse(
            self.fsm_order_id.stock_request_ids.filtered(
                lambda x: x.direction == "inbound"
            )
        )
        self.assertEqual(self.fsm_order_id.scrap_count, 3)
        self.fsm_order_id.stock_request_ids.unlink()
        self.wizard.action_scrap()
        orders = self.env["stock.request.order"].search(
            [("fsm_order_id", "=", self.fsm_order_id.id)]
        )
        # After scrapping all stock requests, no stock request orders should remain
        self.assertEqual(len(orders), 0)
