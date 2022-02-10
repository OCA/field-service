# Copyright (C) 2022 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase


class FSMDeliveryCase(TransactionCase):
    def setUp(self):
        super(FSMDeliveryCase, self).setUp()
        self.SaleOrder = self.env["sale.order"]
        self.test_partner = self.env["res.partner"].create(
            {"name": "Test Partner", "phone": "123", "email": "tp@email.com"}
        )
        self.product_delivery_normal = self.env["product.product"].create(
            {
                "name": "Normal Delivery Charges",
                "invoice_policy": "order",
                "type": "service",
                "list_price": 10.0,
                "categ_id": self.env.ref("delivery.product_category_deliveries").id,
            }
        )
        self.product_cable_management_box = self.env["product.product"].create(
            {
                "name": "Another product to deliver",
                "weight": 1.0,
                "invoice_policy": "order",
            }
        )
        self.pricelist_id = self.env.ref("product.list0")
        self.normal_delivery = self.env["delivery.carrier"].create(
            {
                "name": "Normal Delivery Charges",
                "fixed_price": 10,
                "delivery_type": "fixed",
                "product_id": self.product_delivery_normal.id,
            }
        )
        self.test_location = self.env["fsm.location"].create(
            {
                "name": "Test Location",
                "phone": "123",
                "email": "tp@email.com",
                "partner_id": self.test_partner.id,
                "owner_id": self.test_partner.id,
                "customer_id": self.test_partner.id,
            }
        )
        self.test_order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "date_start": datetime.today(),
                "date_end": datetime.today() + timedelta(hours=2),
                "request_early": datetime.today(),
                "carrier_id": self.normal_delivery.id,
            }
        )

    def test_delivery_stock_move(self):
        self.sale_prepaid = self.SaleOrder.create(
            {
                "partner_id": self.test_partner.id,
                "partner_invoice_id": self.test_partner.id,
                "partner_shipping_id": self.test_partner.id,
                "pricelist_id": self.pricelist_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Cable Management Box",
                            "product_id": self.product_cable_management_box.id,
                            "product_uom_qty": 2,
                            "product_uom": self.env.ref("uom.product_uom_unit").id,
                            "price_unit": 750.00,
                        },
                    )
                ],
            }
        )
        self.sale_prepaid.action_confirm()
        moves = self.sale_prepaid.picking_ids.move_lines
        moves.fsm_order_id = self.test_order.id
        moves._get_new_picking_values()
