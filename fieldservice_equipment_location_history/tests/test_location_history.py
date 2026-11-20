# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError, UserError
from odoo.tests.common import TransactionCase, new_test_user


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

    def _new_equipment(self, serial, location):
        product = self.env["product.product"].create(
            {"name": f"Device {serial}", "is_storable": True, "tracking": "serial"}
        )
        lot = self.env["stock.lot"].create({"name": serial, "product_id": product.id})
        if location:
            self.env["stock.quant"]._update_available_quantity(
                product, location, 1.0, lot_id=lot
            )
        equipment = self.env["fsm.equipment"].create(
            {"name": f"Device {serial}", "product_id": product.id, "lot_id": lot.id}
        )
        return equipment, lot

    def _transfer(self, equipment, from_location, to_location, env=None):
        env = env or self.env
        return env["fsm.equipment.location.history"].create(
            {
                "equipment_id": equipment.id,
                "from_location_id": from_location.id,
                "to_location_id": to_location.id,
            }
        )

    def test_transfer_serial_not_in_source_raises(self):
        equipment, _lot = self._new_equipment("SN-0002", False)
        with self.assertRaisesRegex(UserError, "not available"):
            self._transfer(equipment, self.loc_a, self.loc_b)

    def test_transfer_moves_own_serial_not_another_one(self):
        other_lot = self.env["stock.lot"].create(
            {"name": "SN-0000", "product_id": self.product.id}
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.loc_a, 1.0, lot_id=other_lot
        )
        history = self._transfer(self.equipment, self.loc_a, self.loc_b)
        self.assertEqual(history.picking_id.move_line_ids.lot_id, self.lot)
        self.assertEqual(
            self.env["stock.quant"]._get_available_quantity(
                self.product, self.loc_a, lot_id=other_lot
            ),
            1.0,
        )

    def test_transfer_serial_reserved_elsewhere_raises(self):
        picking_type = self.warehouse.int_type_id
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": self.loc_a.id,
                "location_dest_id": self.loc_b.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Other operation",
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 1.0,
                            "location_id": self.loc_a.id,
                            "location_dest_id": self.loc_b.id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(picking.move_line_ids.lot_id, self.lot)
        with self.assertRaisesRegex(UserError, "reserved"):
            self._transfer(self.equipment, self.loc_a, self.loc_b)

    def test_transfer_uses_company_picking_type(self):
        company = self.env["res.company"].create({"name": "Other Co"})
        self.env.user.company_ids |= company
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", company.id)], limit=1
        )
        dest = self.env["stock.location"].create(
            {
                "name": "Other Bench",
                "location_id": warehouse.view_location_id.id,
                "company_id": company.id,
            }
        )
        equipment, _lot = self._new_equipment("SN-0003", warehouse.lot_stock_id)
        history = self._transfer(equipment, warehouse.lot_stock_id, dest)
        self.assertEqual(history.picking_id.company_id, company)
        self.assertEqual(history.picking_id.picking_type_id.company_id, company)
        self.assertEqual(history.picking_id.picking_type_id.warehouse_id, warehouse)

    def test_transfer_outside_warehouse_falls_back_to_company_type(self):
        source = self.env["stock.location"].create(
            {
                "name": "Loose Shelf",
                "location_id": self.env.ref("stock.stock_location_locations").id,
                "company_id": self.env.company.id,
            }
        )
        equipment, _lot = self._new_equipment("SN-0004", source)
        history = self._transfer(equipment, source, self.loc_b)
        self.assertEqual(history.picking_id.state, "done")
        self.assertEqual(
            history.picking_id.picking_type_id.company_id, self.env.company
        )

    def test_transfer_other_company_not_allowed(self):
        company = self.env["res.company"].create({"name": "Foreign Co"})
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", company.id)], limit=1
        )
        equipment, _lot = self._new_equipment("SN-0005", False)
        user = new_test_user(
            self.env, login="fsm-foreign", groups="fieldservice.group_fsm_user"
        )
        with self.assertRaises(AccessError):
            self._transfer(
                equipment.with_user(user),
                warehouse.lot_stock_id,
                self.loc_b,
                env=self.env(user=user),
            )

    def test_fsm_user_without_stock_rights_can_transfer(self):
        partner = self.env["res.partner"].create({"name": "Bench Owner"})
        fsm_location = self.env["fsm.location"].create(
            {
                "name": "Bench B",
                "owner_id": partner.id,
                "inventory_location_id": self.loc_b.id,
            }
        )
        user = new_test_user(
            self.env, login="fsm-tech", groups="fieldservice.group_fsm_user"
        )
        # With fieldservice_maintenance, equipments inherit maintenance.equipment,
        # whose rule hides non-followed equipments from basic users.
        user.groups_id |= (
            self.env.ref(
                "maintenance.group_equipment_manager", raise_if_not_found=False
            )
            or self.env["res.groups"]
        )
        self.assertFalse(user.has_group("stock.group_stock_user"))
        history = self._transfer(
            self.equipment, self.loc_a, self.loc_b, env=self.env(user=user)
        )
        self.assertEqual(history.sudo().picking_id.state, "done")
        self.assertEqual(self.equipment.location_id, fsm_location)

    def test_equipment_transfer_button(self):
        action = self.equipment.action_create_location_history()
        self.assertEqual(action["res_model"], "fsm.equipment.location.history")
        self.assertEqual(action["context"]["default_equipment_id"], self.equipment.id)
