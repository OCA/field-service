# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestFSMEquipmentType(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Equipment = self.env["fsm.equipment"]
        self.EquipmentType = self.env["fsm.equipment.type"]
        self.equipment = self.Equipment.create({"name": "Equipment"})
        self.equipment_type = self.EquipmentType.create(
            {
                "name": "Equipment Type",
                "code": "KO",
                "description": "Equipment Type Description",
            }
        )

    def test_fsm_equipment_type(self):
        """Test creating new equipment type, and assigning it to an existing equipment."""
        self.equipment.write({"type_id": self.equipment_type.id})
        self.assertEqual(self.equipment_type, self.equipment.type_id)
