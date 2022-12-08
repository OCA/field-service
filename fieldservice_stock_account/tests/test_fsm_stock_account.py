# Copyright (C) 2022 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import datetime

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class FSMStockAccountCase(TransactionCase):
    def setUp(self):
        super(FSMStockAccountCase, self).setUp()
        self.fsm_order = self.env["fsm.order"]
        self.test_location = self.env.ref("fieldservice.test_location")
        self.inv_location = self.env.ref("stock.stock_location_customers")
        self.test_person = self.env.ref("fieldservice.test_person")
        self.test_partner = self.env.ref("fieldservice.test_partner")

    def test_fsm_order(self):
        self.test_person.partner_id.supplier_rank = 1
        self.test_location.inventory_location_id = self.inv_location.id
        fsm_order = self.fsm_order.create(
            {"location_id": self.test_location.id, "person_id": self.test_person.id}
        )
        fsm_order2 = self.fsm_order.create(
            {"location_id": self.test_location.id, "person_id": self.test_person.id}
        )

        self.env["stock.picking.type"].create(
            {
                "name": "Stock Request wh",
                "sequence_id": self.env.ref("stock_request.seq_stock_request_order").id,
                "code": "stock_request_order",
                "sequence_code": "SRO",
                "warehouse_id": fsm_order.warehouse_id.id,
            }
        )
        self.product_1 = self.env["product.product"].create(
            {
                "name": "Product 1",
                "type": "product",
                "categ_id": self.env.ref("product.product_category_all").id,
            }
        )
        SR_1 = self.env["stock.request"].create(
            {
                "warehouse_id": fsm_order.warehouse_id.id,
                "location_id": fsm_order.inventory_location_id.id,
                "product_id": self.product_1.id,
                "product_uom_qty": 1,
                "product_uom_id": self.product_1.uom_id.id,
                "fsm_order_id": fsm_order.id,
                "direction": "outbound",
                "expected_date": datetime.datetime.now(),
                "picking_policy": "direct",
            }
        )
        SR_2 = self.env["stock.request"].create(
            {
                "warehouse_id": fsm_order2.warehouse_id.id,
                "location_id": fsm_order2.inventory_location_id.id,
                "product_id": self.product_1.id,
                "product_uom_qty": 1,
                "product_uom_id": self.product_1.uom_id.id,
                "fsm_order_id": fsm_order2.id,
                "direction": "outbound",
                "expected_date": datetime.datetime.now(),
                "picking_policy": "direct",
            }
        )
        fsm_order.stock_request_ids = [(6, 0, SR_1.ids)]
        fsm_order.action_request_submit()
        SR_1.action_confirm()
        fsm_order.account_create_invoice()
        fsm_order2.stock_request_ids = [(6, 0, SR_2.ids)]
        fsm_order2.action_request_submit()
        SR_2.action_confirm()
        fsm_order2.account_no_invoice()
        fsm_order2.bill_to = "contact"
        with self.assertRaises(UserError):
            fsm_order2.account_no_invoice()
        fsm_order2.customer_id = self.test_partner.id
        fsm_order2.account_no_invoice()
