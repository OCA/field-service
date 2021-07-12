# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.tests.common import Form, TransactionCase


class TestStockPicking(TransactionCase):
    def setUp(self):
        super(TestStockPicking, self).setUp()

        self.Order = self.env["fsm.order"]
        self.test_location = self.env.ref("fieldservice.test_location")
        self.uom_kg = self.env.ref("uom.product_uom_kgm")
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.customer_location = self.env.ref("stock.stock_location_customers")

        self.product = self.env["product.product"].create(
            {
                "name": "Product KG",
                "uom_id": self.uom_kg.id,
                "uom_po_id": self.uom_kg.id,
                "type": "product",
            }
        )
        self.picking_type_id = self.env.ref(
            "fieldservice_vehicle_stock.picking_type_output_to_vehicle"
        )
        self.fsm_vehicle_id = self.env["fsm.vehicle"].create(
            {
                "name": "Vehicle 1",
                "inventory_location_id": self.stock_location.id,
            }
        )
        self.fsm_vehicle2_id = self.env["fsm.vehicle"].create(
            {
                "name": "Vehicle 2",
                "inventory_location_id": self.stock_location.id,
            }
        )
        self.picking_out = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_id.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "fsm_vehicle_id": self.fsm_vehicle_id.id,
            }
        )

        self.move = self.env["stock.move"].create(
            {
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom_qty": 2.5,
                "product_uom": self.product.uom_id.id,
                "picking_id": self.picking_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )

    def test_action_assign(self):
        self.picking_out.action_confirm()
        self.picking_out.action_assign()
        for move in self.picking_out.move_lines:
            self.assertEqual(move.state, "confirmed")

    def test_prepare_fsm_values(self):

        # Create an Orders
        view_id = "fieldservice.fsm_order_form"
        hours_diff = 100
        with Form(self.Order, view=view_id) as f:
            f.location_id = self.test_location
            f.date_start = fields.Datetime.today()
            f.date_end = f.date_start + timedelta(hours=hours_diff)
            f.request_early = fields.Datetime.today()
            f.vehicle_id = self.fsm_vehicle2_id
        order = f.save()

        res = self.picking_out.prepare_fsm_values(order)
        self.assertEqual(res["fsm_vehicle_id"], self.fsm_vehicle2_id.id)
