# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestFSMRepairCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestFSMRepairCommon, cls).setUpClass()
        cls.test_location = cls.env.ref("fieldservice.test_location")
        cls.stock_location = cls.env.ref("stock.stock_location_customers")
        cls.FSMOrder = cls.env["fsm.order"]
        cls.OrderType = cls.env["fsm.order.type"].create(
            {"name": "Test1", "internal_type": "repair"}
        )
        cls.product1 = cls.env["product.product"].create(
            {"name": "Product A", "type": "product"}
        )
        cls.lot1 = cls.env["stock.lot"].create(
            {
                "name": "sn11",
                "product_id": cls.product1.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.equipment = cls.env["fsm.equipment"].create(
            {
                "name": "test equipment",
                "product_id": cls.product1.id,
                "lot_id": cls.lot1.id,
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
