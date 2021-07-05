# Copyright (C) 2020, Brian McMaster
# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestFSMStockCommon(TransactionCase):
    def setUp(self):
        super(TestFSMStockCommon, self).setUp()
        self.location = self.env["fsm.location"]
        self.FSMOrder = self.env["fsm.order"]
        self.Product = self.env["product.product"]

        self.stock_cust_loc = self.env.ref("stock.stock_location_customers")
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.customer_location = self.env.ref("stock.stock_location_customers")
        self.test_location = self.env.ref("fieldservice.test_location")
        self.partner_1 = (
            self.env["res.partner"]
            .with_context(tracking_disable=True)
            .create({"name": "Partner 1"})
        )
        self.customer = self.env["res.partner"].create({"name": "SuperPartner"})

    def test_fsm_orders(self):
        """Test creating new workorders, and test following functions."""
        # Create an Orders
        hours_diff = 100
        date_start = fields.Datetime.today()

        order = self.FSMOrder.create(
            {
                "location_id": self.test_location.id,
                "date_start": date_start,
                "date_end": date_start + timedelta(hours=hours_diff),
                "request_early": fields.Datetime.today(),
            }
        )
        self.picking = self.env["stock.picking"].create(
            {
                "location_dest_id": self.stock_location.id,
                "location_id": self.customer_location.id,
                "partner_id": self.customer.id,
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "fsm_order_id": order.id,
            }
        )
        self.out_picking = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "partner_id": self.customer.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "fsm_order_id": order.id,
            }
        )
        order._compute_picking_ids()
        order.location_id._onchange_fsm_parent_id()
        order._default_warehouse_id()
        order.action_view_delivery()
        order.action_view_returns()
