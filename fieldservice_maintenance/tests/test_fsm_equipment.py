# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestFSMEquipment(TransactionCase):
    def setUp(self):
        super(TestFSMEquipment, self).setUp()
        self.maintenance_team = self.env["maintenance.team"].create(
            {"name": "Test Maintenance Team", "company_id": self.env.user.company_id.id}
        )
        self.test_equipment = self.env["fsm.equipment"]

    def test_equipment_create_unlink(self):
        fsm_equipment = self.test_equipment.create(
            {
                "name": "Test Equipment",
                "company_id": self.env.user.company_id.id,
                "maintenance_team_id": self.maintenance_team.id,
            }
        )
        maintenance_equipment = self.env["maintenance.equipment"].search(
            [("name", "=", fsm_equipment.name), ("is_fsm_equipment", "=", True)]
        )
        self.assertTrue(maintenance_equipment)
        fsm_equipment.unlink()
        self.assertFalse(maintenance_equipment.is_fsm_equipment)
