# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author: Italo Lopes <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestFSMEquipmentStockReturn(TransactionCase):
    def setUp(self):
        super().setUp()
        self.fsm_test_location = self.env.ref("fieldservice.test_location")
        self.customer_stock_location = self.env.ref("stock.stock_location_customers")

        self.fsm_location_1 = self.env.ref("fieldservice.location_1")
        self.stock_location2 = self.env["stock.location"].create(
            {"name": "Stock Customer Location 2", "usage": "customer"}
        )
        self.fsm_location_1.write(
            {
                "name": "Test Location 2",
                "inventory_location_id": self.stock_location2.id,
            }
        )

        self.FSMOrder = self.env["fsm.order"]
        self.FSMEquip = self.env["fsm.equipment"]
        self.OrderType = self.env.ref(
            "fieldservice_equipment_stock_return.fsm_order_type_return"
        )
        self.OrderType.picking_type_id = (
            self.env["stock.picking.type"]
            .search([("code", "=", "incoming")], limit=1)
            .id
        )
        self.product1 = self.env["product.product"].create(
            {"name": "Product A", "type": "product"}
        )
        self.lot1 = self.env["stock.lot"].create(
            {
                "name": "sn11",
                "product_id": self.product1.id,
                "company_id": self.env.company.id,
                "location_id": self.customer_stock_location.id,
            }
        )
        self.equipment = self.FSMEquip.create(
            {
                "name": "test equipment",
                "product_id": self.product1.id,
                "lot_id": self.lot1.id,
            }
        )

    def test_00_equipment_return(self):
        """Test return from equipment."""
        equipment_create_vals = self.equipment.create_equipment_order_return()
        self.assertEqual(equipment_create_vals["res_model"], "fsm.order")
        self.assertEqual(
            equipment_create_vals["context"]["default_equipment_id"], self.equipment.id
        )
        self.assertEqual(
            equipment_create_vals["context"]["default_type"], self.OrderType.id
        )

    def test_01_fsmorder_equipment_return(self):
        """Test creating new fsm order."""
        self.equipment.current_stock_location_id = self.customer_stock_location.id
        fsm_order_return = self.FSMOrder.create(
            {
                "type": self.OrderType.id,
                "location_id": self.fsm_test_location.id,
                "equipment_id": self.equipment.id,
            }
        )
        picking = fsm_order_return.picking_ids
        self.assertEqual(picking.picking_type_id, fsm_order_return.type.picking_type_id)
        self.assertEqual(picking.group_id, fsm_order_return.procurement_group_id)
        self.assertEqual(picking.fsm_order_id, fsm_order_return)

    def get_validate_message(self, error_type):
        if error_type == "no_location":
            return "Impossible to find the equipment current location."
        elif error_type == "no_picking_type":
            return (
                "You must set a Picking Type on the order type "
                "and an equipment on the order"
            )
        elif error_type == "no_order_type":
            return "No return order type found."
        elif error_type == "no_equipment":
            return (
                "You must set a Picking Type on the order type "
                "and an equipment on the order"
            )

    def test_02_equipment_return_errors_no_location(self):
        """Test creating new fsm order with known errors."""

        message = self.get_validate_message("no_location")
        with self.assertRaisesRegex(ValidationError, message):
            self.FSMOrder.create(
                {
                    "type": self.OrderType.id,
                    "location_id": self.fsm_test_location.id,
                    "equipment_id": self.equipment.id,
                }
            )

    def test_03_equipment_return_errors_no_picking_type(self):
        """Test creating new fsm order with known errors."""
        message = self.get_validate_message("no_picking_type")
        self.OrderType.picking_type_id = False
        with self.assertRaisesRegex(ValidationError, message):
            self.FSMOrder.create(
                {
                    "type": self.OrderType.id,
                    "location_id": self.fsm_test_location.id,
                    "equipment_id": self.equipment.id,
                }
            )

    def test_04_equipment_return_errors_no_order_type(self):
        """Test creating new fsm order with known errors."""
        message = self.get_validate_message("no_order_type")
        self.OrderType.unlink()
        with self.assertRaisesRegex(ValidationError, message):
            self.equipment.create_equipment_order_return()

    def test_05_equipment_return_errors_no_equipment(self):
        """Test creating new fsm order with known errors."""
        message = self.get_validate_message("no_equipment")
        with self.assertRaisesRegex(ValidationError, message):
            self.FSMOrder.create(
                {
                    "type": self.OrderType.id,
                    "location_id": self.fsm_test_location.id,
                }
            )

    def test_06_equipment_return_errors_using_fsm_current_location(self):
        """Test creating new fsm order with known errors."""
        self.equipment.current_location_id = self.fsm_location_1.id
        fsm_order_return = self.FSMOrder.create(
            {
                "type": self.OrderType.id,
                "location_id": self.fsm_location_1.id,
                "equipment_id": self.equipment.id,
            }
        )
        picking = fsm_order_return.picking_ids
        self.assertEqual(picking.picking_type_id, fsm_order_return.type.picking_type_id)
        self.assertEqual(picking.group_id, fsm_order_return.procurement_group_id)
        self.assertEqual(picking.fsm_order_id, fsm_order_return)
        self.assertEqual(picking.location_id, self.stock_location2)
