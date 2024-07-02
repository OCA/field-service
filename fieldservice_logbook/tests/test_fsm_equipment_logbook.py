# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo import fields
from odoo.tests import RecordCapturer
from odoo.tests.common import Form, TransactionCase


@freeze_time("2024-01-01")
class FSMEquipmentLogbook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.Equipment = cls.env["fsm.equipment"]
        cls.Location = cls.env["fsm.location"]
        cls.Order = cls.env["fsm.order"]
        cls.Logbook = cls.env["fsm.equipment.logbook"]
        cls.test_location = cls.env.ref("fieldservice.test_location")
        cls.current_location = cls.env.ref("fieldservice.location_1")
        cls.equipment_stage_1 = cls.env.ref("fieldservice.equipment_stage_1")
        cls.equipment_stage_2 = cls.env.ref("fieldservice.equipment_stage_2")
        cls.equipment_stage_3 = cls.env.ref("fieldservice.equipment_stage_3")

    def test_fsm_equipment(self):
        """Test createing new equipment
        - Default stage -> Create a log in logbook
        - Change stage -> Create a log in logbook
        """
        # Create an equipment
        view_id = "fieldservice.fsm_equipment_form_view"
        with Form(self.Equipment, view=view_id) as f:
            f.name = "Equipment 1"
            f.current_location_id = self.current_location
            f.location_id = self.test_location
        equipment = f.save()
        # Test initial stage
        self.assertEqual(equipment.stage_id, self.equipment_stage_1)
        self.assertEqual(equipment.equipment_logs_count, 1)
        self.assertRecordValues(
            equipment.equipment_logs_ids,
            [
                {
                    "origin_status": self.equipment_stage_1.name,
                    "note": "Equipment 1",
                    "res_id": equipment.id,
                    "equipment_status": self.equipment_stage_1.name,
                    "location_id": self.test_location.id,
                    "equipment_id": equipment.id,
                    "type": "equipment",
                    "res_model": "fsm.equipment",
                    "event_date": fields.Datetime.now(),
                }
            ],
        )

        # Test change state
        equipment.next_stage()
        self.assertEqual(equipment.stage_id, self.equipment_stage_2)
        self.assertEqual(equipment.equipment_logs_count, 2)
        with RecordCapturer(self.Logbook, []) as log:
            equipment.write(
                {
                    "stage_id": self.equipment_stage_3.id,
                    "location_id": self.current_location.id,
                }
            )
        log.records.ensure_one()
        self.assertEqual(log.records.equipment_status, self.equipment_stage_3.name)
        self.assertEqual(log.records.location_id, self.current_location)
