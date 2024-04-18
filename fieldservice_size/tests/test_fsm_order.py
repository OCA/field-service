# Copyright (C) 2020 - Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestFSMSize(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Size = cls.env["fsm.size"]
        cls.Location_size = cls.env["fsm.location.size"]
        cls.Type = cls.env["fsm.order.type"]
        cls.Order = cls.env["fsm.order"]
        cls.UOM = cls.env.ref("uom.product_uom_unit")
        cls.type_a = cls.Type.create({"name": "Type A"})
        cls.size_a = cls.Size.create(
            {
                "name": "Size A 1",
                "type_id": cls.type_a.id,
                "uom_id": cls.UOM.id,
                "is_order_size": True,
            }
        )
        cls.test_location = cls.env.ref("fieldservice.test_location")

    def test_one_size_per_type(self):
        with self.assertRaises(ValidationError) as e:
            self.Size.create(
                {
                    "name": "Size A 2",
                    "type_id": self.type_a.id,
                    "uom_id": self.UOM.id,
                    "is_order_size": True,
                }
            )
        self.assertEqual(
            e.exception.args[0], "Only one default order size per type is allowed."
        )

    def test_order_onchange_location(self):
        self.Location_size.create(
            {
                "size_id": self.size_a.id,
                "quantity": 24.5,
                "location_id": self.test_location.id,
            }
        )
        order = self.Order.create(
            {
                "type": self.type_a.id,
                "location_id": self.test_location.id,
            }
        )
        order._onchange_location_id_customer()
        order.onchange_type()
        order.onchange_size_id()
        self.assertTrue(order.size_id, self.size_a.id)
        self.assertTrue(order.size_value, 24.5)
        self.assertTrue(order.size_uom, self.size_a.uom_id)
