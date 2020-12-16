# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestMaintenanceEquipment(TransactionCase):
    def setUp(self):
        super(TestMaintenanceEquipment, self).setUp()
        self.test_location = self.env.ref("fieldservice.test_location")
        self.maintenance_team = self.env["maintenance.team"].create(
            {"name": "Test Maintenance Team", "company_id": self.env.user.company_id.id}
        )
        self.maintenance_order_type = self.env["fsm.order.type"].create(
            {"name": "Maintenance Request", "internal_type": "maintenance"}
        )
        self.test_equipment = self.env["fsm.equipment"].create(
            {
                "name": "Test Equipment",
                "company_id": self.env.user.company_id.id,
                "maintenance_team_id": self.maintenance_team.id,
                "current_location_id": self.test_location.id,
            }
        )
        self.test_maintenance_request = self.env["maintenance.request"]

    def test_maintenance_request_create(self):
        maintenance_equipment = self.env["maintenance.equipment"].search(
            [("name", "=", self.test_equipment.name), ("is_fsm_equipment", "=", True)]
        )
        maintenance_request = self.test_maintenance_request.create(
            {
                "name": "Test Maintenance Request",
                "maintenance_team_id": self.maintenance_team.id,
                "equipment_id": maintenance_equipment.id,
            }
        )
        fsm_order = self.env["fsm.order"].search(
            [
                ("type", "=", self.maintenance_order_type.id),
                ("equipment_id", "=", self.test_equipment.id),
                ("request_id", "=", maintenance_request.id),
            ]
        )
        self.assertTrue(fsm_order)
