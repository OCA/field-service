# Copyright 2020, Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestFSMStageValidation(TransactionCase):
    def setUp(self):
        super().setUp()
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))
        self.stage = self.env["fsm.stage"]
        self.fsm_order = self.env["fsm.order"]
        self.fsm_person = self.env["fsm.person"]
        self.fsm_location = self.env["fsm.location"]
        self.fsm_equipment = self.env["fsm.equipment"]
        self.ir_model_fields = self.env["ir.model.fields"]

        # Get some fields to use in the stages
        self.order_field = self.ir_model_fields.search(
            [("model", "=", "fsm.order"), ("name", "=", "description")]
        )
        self.person_field = self.ir_model_fields.search(
            [("model", "=", "fsm.person"), ("name", "=", "mobile")]
        )
        self.location_field = self.ir_model_fields.search(
            [("model", "=", "fsm.location"), ("name", "=", "direction")]
        )
        self.equipment_field = self.ir_model_fields.search(
            [("model", "=", "fsm.equipment"), ("name", "=", "notes")]
        )

        # For each model type, create a default stage and a stage
        # which will apply field validation
        # Order Stages
        self.stage_order_default = self.stage.create(
            {
                "name": "Order Stage Default",
                "stage_type": "order",
                "is_default": True,
                "sequence": "10",
            }
        )
        self.stage_order = self.stage.create(
            {
                "name": "Order Stage Validate",
                "stage_type": "order",
                "validate_field_ids": [(6, 0, [self.order_field.id])],
                "sequence": "11",
            }
        )
        # Person Stages
        self.stage_person_default = self.stage.create(
            {
                "name": "Person Stage Default",
                "stage_type": "worker",
                "is_default": True,
                "sequence": "10",
            }
        )
        self.stage_person = self.stage.create(
            {
                "name": "Person Stage Validate",
                "stage_type": "worker",
                "validate_field_ids": [(6, 0, [self.person_field.id])],
                "sequence": "11",
            }
        )
        # Location Stages
        self.stage_location_default = self.stage.create(
            {
                "name": "Location Stage Default",
                "stage_type": "location",
                "is_default": True,
                "sequence": "10",
            }
        )
        self.stage_location = self.stage.create(
            {
                "name": "Location Stage Validate",
                "stage_type": "location",
                "validate_field_ids": [(6, 0, [self.location_field.id])],
                "sequence": "11",
            }
        )
        # Equipment Stages
        self.stage_equipment_default = self.stage.create(
            {
                "name": "Equipment Stage Default",
                "stage_type": "equipment",
                "is_default": True,
                "sequence": "10",
            }
        )
        self.stage_equipment = self.stage.create(
            {
                "name": "Equipment Stage Validate",
                "stage_type": "equipment",
                "validate_field_ids": [(6, 0, [self.equipment_field.id])],
                "sequence": "11",
            }
        )

        # Create a person
        self.person_01 = self.fsm_person.create(
            {
                "name": "FSM Worker 01",
                "partner_id": self.env["res.partner"]
                .create({"name": "Worker 01 Partner"})
                .id,
                "stage_id": self.stage_person_default.id,
            }
        )
        # Create a location
        self.location_01 = self.fsm_location.create(
            {
                "name": "Location 01",
                "owner_id": self.env["res.partner"]
                .create({"name": "Location 01 Partner"})
                .id,
                "stage_id": self.stage_location_default.id,
            }
        )
        # Create an Equipment
        self.equipment_01 = self.fsm_equipment.create(
            {
                "name": "Equipment 01",
                "current_location_id": self.location_01.id,
                "stage_id": self.stage_equipment_default.id,
            }
        )
        # Create an Order
        self.order_01 = self.fsm_order.create({"location_id": self.location_01.id})

    def get_validate_message(self, stage):
        stage_name = stage.name
        field_name = fields.first(stage.validate_field_ids).name
        return 'Cannot move to stage "%s" until the "%s" field is set.' % (
            stage_name,
            field_name,
        )

    def test_fsm_stage_validation(self):

        # Validate the stage computes the correct model type
        self.assertEqual(
            self.stage_order.stage_type_model_id,
            self.env["ir.model"].search([("model", "=", "fsm.order")]),
            "FSM Stage model is not computed correctly",
        )
        validate_message = self.get_validate_message(self.stage_equipment)
        # Validate the Equipment cannot move to next stage
        with self.assertRaisesRegex(ValidationError, validate_message):
            self.equipment_01.next_stage()

        # Update the Equipment notes field and validate it goes to next stage
        self.equipment_01.notes = "Equipment service note"
        self.equipment_01.next_stage()
        self.assertEqual(
            self.equipment_01.stage_id,
            self.stage_equipment,
            "FSM Equipment did not progress to correct stage",
        )
        validate_message = self.get_validate_message(self.stage_location)
        # Validate the Location cannot move to next stage
        with self.assertRaisesRegex(ValidationError, validate_message):
            self.location_01.next_stage()

        # Update the Location directions field and validate it goes to next stage
        self.location_01.direction = "Location direction note"
        self.location_01.next_stage()
        self.assertEqual(
            self.location_01.stage_id,
            self.stage_location,
            "FSM Location did not progress to correct stage",
        )
        validate_message = self.get_validate_message(self.stage_person)
        # Validate the Person cannot move to next stage
        with self.assertRaisesRegex(ValidationError, validate_message):
            self.person_01.next_stage()

        # Update the Person mobile field and validate it goes to next stage
        self.person_01.mobile = "1-888-888-8888"
        self.person_01.next_stage()
        self.assertEqual(
            self.person_01.stage_id,
            self.stage_person,
            "FSM Person did not progress to correct stage",
        )
        validate_message = self.get_validate_message(self.stage_order)
        # Validate the Order cannot move to stage which requires validation
        with self.assertRaisesRegex(ValidationError, validate_message):
            self.order_01.write({"stage_id": self.stage_order.id})

        # Update the Order description field and validate it goes to next stage
        self.order_01.description = "Complete the work order"
        self.order_01.write({"stage_id": self.stage_order.id})
        self.assertEqual(
            self.order_01.stage_id,
            self.stage_order,
            "FSM Order did not progress to correct stage",
        )
