# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestEquipmentLocationHistory(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["res.config.settings"].create(
            {"group_stock_multi_locations": True}
        ).execute()
        cls.warehouse = cls.env["stock.warehouse"].search([], limit=1)
        cls.loc_a = cls.warehouse.lot_stock_id
        cls.loc_b = cls.env["stock.location"].create(
            {"name": "Bench B", "location_id": cls.loc_a.location_id.id}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Tracked Device",
                "is_storable": True,
                "tracking": "serial",
            }
        )
        cls.lot = cls.env["stock.lot"].create(
            {"name": "SN-0001", "product_id": cls.product.id}
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.loc_a, 1.0, lot_id=cls.lot
        )
        cls.equipment = cls.env["fsm.equipment"].create(
            {
                "name": "Device SN-0001",
                "product_id": cls.product.id,
                "lot_id": cls.lot.id,
            }
        )

    def test_transfer_moves_serial(self):
        history = self.env["fsm.equipment.location.history"].create(
            {
                "equipment_id": self.equipment.id,
                "from_location_id": self.loc_a.id,
                "to_location_id": self.loc_b.id,
                "type_selection": "inbound",
            }
        )
        self.assertEqual(history.picking_id.state, "done")
        quant = self.env["stock.quant"].search(
            [
                ("lot_id", "=", self.lot.id),
                ("location_id", "=", self.loc_b.id),
                ("quantity", ">", 0),
            ]
        )
        self.assertTrue(quant, "serial must be at destination after transfer")
        self.assertIn(history, self.equipment.location_history_ids)

    def test_transfer_updates_fsm_location(self):
        partner = self.env["res.partner"].create({"name": "FSM Loc Partner"})
        fsm_location = self.env["fsm.location"].create(
            {
                "name": "Bench B",
                "owner_id": partner.id,
                "inventory_location_id": self.loc_b.id,
            }
        )
        self.env["fsm.equipment.location.history"].create(
            {
                "equipment_id": self.equipment.id,
                "from_location_id": self.loc_a.id,
                "to_location_id": self.loc_b.id,
            }
        )
        self.assertEqual(self.equipment.location_id, fsm_location)

    def test_transfer_without_serial_raises(self):
        bare_equipment = self.env["fsm.equipment"].create({"name": "No Serial"})
        with self.assertRaises(UserError):
            self.env["fsm.equipment.location.history"].create(
                {
                    "equipment_id": bare_equipment.id,
                    "from_location_id": self.loc_a.id,
                    "to_location_id": self.loc_b.id,
                }
            )

    def test_transfer_without_internal_picking_type_raises(self):
        self.env["stock.picking.type"].search(
            [("code", "=", "internal")]
        ).active = False
        with self.assertRaises(UserError):
            self.env["fsm.equipment.location.history"].create(
                {
                    "equipment_id": self.equipment.id,
                    "from_location_id": self.loc_a.id,
                    "to_location_id": self.loc_b.id,
                }
            )

    def test_transfer_without_reservable_stock_creates_move_line(self):
        product = self.env["product.product"].create(
            {
                "name": "Unstocked Device",
                "is_storable": True,
                "tracking": "serial",
            }
        )
        lot = self.env["stock.lot"].create(
            {"name": "SN-0002", "product_id": product.id}
        )
        equipment = self.env["fsm.equipment"].create(
            {
                "name": "Device SN-0002",
                "product_id": product.id,
                "lot_id": lot.id,
            }
        )
        history = self.env["fsm.equipment.location.history"].create(
            {
                "equipment_id": equipment.id,
                "from_location_id": self.loc_a.id,
                "to_location_id": self.loc_b.id,
            }
        )
        self.assertEqual(history.picking_id.state, "done")
        self.assertEqual(history.picking_id.move_line_ids.lot_id, lot)

    def test_equipment_transfer_button(self):
        action = self.equipment.action_create_location_history()
        self.assertEqual(action["res_model"], "fsm.equipment.location.history")
        self.assertEqual(action["context"]["default_equipment_id"], self.equipment.id)
