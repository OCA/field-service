# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase


class FSMEquipment(TransactionCase):
    def setUp(self):
        super(FSMEquipment, self).setUp()
        self.Equipment = self.env["fsm.equipment"]
        self.test_location = self.env.ref("fieldservice.test_location")
        self.test_territory = self.env.ref("base_territory.test_territory")
        self.test_branch = self.env.ref("base_territory.test_branch")
        self.test_district = self.env.ref("base_territory.test_district")
        self.test_region = self.env.ref("base_territory.test_region")
        self.current_location = self.env.ref("fieldservice.location_1")

    def test_fsm_equipment(self):
        """ Test createing new equipment
            - Default stage
            - Onchange location
            - Change stage
        """
        # Create an equipment
        view_id = "fieldservice.fsm_equipment_form_view"
        with Form(self.Equipment, view=view_id) as f:
            f.name = "Equipment 1"
            f.current_location_id = self.current_location
            f.location_id = self.test_location
        equipment = f.save()
        # Test onchange location
        self.assertEqual(self.test_territory, equipment.territory_id)
        self.assertEqual(self.test_branch, equipment.branch_id)
        self.assertEqual(self.test_district, equipment.district_id)
        self.assertEqual(self.test_region, equipment.region_id)
        # Test initial stage
        self.assertEqual(
            equipment.stage_id, self.env.ref("fieldservice.equipment_stage_1")
        )
        # Test change state
        equipment.next_stage()
        self.assertEqual(
            equipment.stage_id, self.env.ref("fieldservice.equipment_stage_2")
        )
        equipment.next_stage()
        self.assertEqual(
            equipment.stage_id, self.env.ref("fieldservice.equipment_stage_3")
        )
        self.assertTrue(equipment.hide)  # hide as max stage
        equipment.previous_stage()
        self.assertEqual(
            equipment.stage_id, self.env.ref("fieldservice.equipment_stage_2")
        )
