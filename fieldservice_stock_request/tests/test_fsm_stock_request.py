# Copyright (C) 2020, Brian McMaster
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import datetime

from odoo.addons.fieldservice_stock.tests.common import TestFSMStockCommon


class TestFSMStockRequest(TestFSMStockCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # disable tracking in test
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Setup for Stock Request
        cls.StockRequest = cls.env["stock.request"]
        cls.StockRequestOrder = cls.env["stock.request.order"]

        cls.product_1 = cls.Product.create({
            "name": "Product 1",
            "type": "product",
            "categ_id": cls.env.ref("product.product_category_all").id,
        })
        cls.product_2 = cls.Product.create({
            "name": "Product 2",
            "type": "product",
            "categ_id": cls.env.ref("product.product_category_all").id,
        })

    def test_fsm_order_stock_request(self):
        # Create a new FS Order and add to it some SR
        FSO = self.FSMOrder.create({
            "location_id": self.fsm_location_1.id,
        })

        SR_1 = self.StockRequest.create({
            "warehouse_id": FSO.warehouse_id.id,
            "location_id": FSO.inventory_location_id.id,
            "product_id": self.product_1.id,
            "product_uom_qty": 1,
            "product_uom_id": self.product_1.uom_id.id,
            "fsm_order_id": FSO.id,
            "direction": "outbound",
            "expected_date": datetime.datetime.now(),
            "picking_policy": "direct",
        })
        # After create the SR linked to FSO, validate a SRO
        # was created and linked to this FSO
        SRO = self.StockRequestOrder.search([
            ("fsm_order_id", "=", FSO.id),
            ("warehouse_id", "=", FSO.warehouse_id.id)
        ])
        self.assertTrue(SRO)

        # Add a second SR to the FSO
        SR_2 = self.StockRequest.create({
            "warehouse_id": FSO.warehouse_id.id,
            "location_id": FSO.inventory_location_id.id,
            "product_id": self.product_2.id,
            "product_uom_qty": 4,
            "product_uom_id": self.product_2.uom_id.id,
            "fsm_order_id": FSO.id,
            "direction": "outbound",
            "expected_date": datetime.datetime.now(),
            "picking_policy": "direct",
        })
        # After create the 2nd SR linked to same FSO, validate
        # this SR is assigned to the same SRO
        self.assertEqual(SR_2.order_id, SRO)

        # Submit the SRs from FSO. Confirm FSO request, SR & SRO are submitted
        FSO.action_request_submit()
        self.assertEqual(FSO.request_stage, "submitted")
        self.assertEqual(SR_1.state, "submitted")
        self.assertEqual(SR_2.state, "submitted")
        self.assertEqual(SRO.state, "submitted")

        # Cancel the SRs from FSO. Confirm SR are cancelled
        FSO.action_request_cancel()
        self.assertEqual(FSO.request_stage, "cancel")
        self.assertEqual(SR_1.state, "cancel")
        self.assertEqual(SR_2.state, "cancel")
        self.assertEqual(SRO.state, "cancel")

        # Set the SR to draft. Confirm SR are draft
        FSO.action_request_draft()
        self.assertEqual(FSO.request_stage, "draft")
        self.assertEqual(SR_1.state, "draft")
        self.assertEqual(SR_2.state, "draft")
        self.assertEqual(SRO.state, "draft")
