# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestFSMRepairCommon(TransactionCase):
    def setUp(self):
        super().setUp()
        self.test_location = self.env.ref("fieldservice.test_location")
        self.stock_location = self.env.ref("stock.stock_location_customers")
        self.FSMOrder = self.env["fsm.order"]
        self.OrderType = self.env["fsm.order.type"].create(
            {"name": "Test1", "internal_type": "repair"}
        )
        self.product1 = self.env["product.product"].create(
            {"name": "Product A", "type": "product"}
        )
        self.lot1 = self.env["stock.lot"].create(
            {
                "name": "sn11",
                "product_id": self.product1.id,
                "company_id": self.env.company.id,
            }
        )
        self.equipment = self.env["fsm.equipment"].create(
            {
                "name": "test equipment",
                "product_id": self.product1.id,
                "lot_id": self.lot1.id,
            }
        )

    def test_fsm_orders(self):
        """Test creating new workorders, and test following functions."""
        # Create an Orders
        hours_diff = 100
        date_start = fields.Datetime.today()
        with self.assertRaises(ValidationError):
            self.FSMOrder.create(
                {
                    "type": self.OrderType.id,
                    "location_id": self.test_location.id,
                    "equipment_id": self.equipment.id,
                    "date_start": date_start,
                    "date_end": date_start + timedelta(hours=hours_diff),
                    "request_early": fields.Datetime.today(),
                }
            )
        self.equipment.current_stock_location_id = self.stock_location.id
        self.FSMOrder.create(
            {
                "type": self.OrderType.id,
                "location_id": self.test_location.id,
                "equipment_id": self.equipment.id,
                "date_start": date_start,
                "date_end": date_start + timedelta(hours=hours_diff),
                "request_early": fields.Datetime.today(),
            }
        )
