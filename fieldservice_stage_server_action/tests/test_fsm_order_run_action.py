# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import RecordCapturer, TransactionCase


class TestFSMOrderRunAction(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.FSMEquipment = cls.env["fsm.equipment"]
        cls.FSMLocation = cls.env["fsm.location"]
        cls.FSMOrders = cls.env["fsm.order"]
        cls.FSMPerson = cls.env["fsm.person"]
        cls.FSMStage = cls.env["fsm.stage"]
        cls.FSMTag = cls.env["fsm.tag"]
        cls.ServerAction = cls.env["ir.actions.server"]
        # Mail Activity Type
        cls.activity_type = cls.env["mail.activity.type"].create({"name": "To Do"})
        # Phone Number
        cls.phone = "070-070-070"
        # Equipment
        cls.server_action_equipment = cls.ServerAction.create(
            {
                "name": "Equipment Server Action",
                "model_id": cls.env.ref("fieldservice.model_fsm_equipment").id,
                "state": "next_activity",
                "activity_user_field_name": "user_id",
                "activity_type_id": cls.activity_type.id,
                "activity_user_type": "generic",
            }
        )
        cls.stage_equipment_1 = cls.FSMStage.create(
            {
                "name": "Equipment Stage 1",
                "stage_type": "equipment",
                "action_id": cls.server_action_equipment.id,
                "sequence": 10,
            }
        )
        cls.stage_equipment_2 = cls.FSMStage.create(
            {
                "name": "Equipment Stage 2",
                "stage_type": "equipment",
                "action_id": cls.server_action_equipment.id,
                "sequence": 11,
            }
        )
        # Location
        cls.server_action_location = cls.ServerAction.create(
            {
                "name": "Location Server Action",
                "model_id": cls.env.ref("fieldservice.model_fsm_location").id,
                "state": "next_activity",
                "activity_user_field_name": "user_id",
                "activity_type_id": cls.activity_type.id,
                "activity_user_type": "generic",
            }
        )
        cls.stage_location_1 = cls.FSMStage.create(
            {
                "name": "Location Stage 1",
                "stage_type": "location",
                "action_id": cls.server_action_location.id,
                "sequence": 12,
            }
        )
        cls.stage_location_2 = cls.FSMStage.create(
            {
                "name": "Location Stage 2",
                "stage_type": "location",
                "action_id": cls.server_action_location.id,
                "sequence": 13,
            }
        )
        # Order
        cls.server_action_order = cls.ServerAction.create(
            {
                "name": "Order Server Action",
                "model_id": cls.env.ref("fieldservice.model_fsm_order").id,
                "state": "next_activity",
                "activity_user_field_name": "user_id",
                "activity_type_id": cls.activity_type.id,
                "activity_user_type": "generic",
            }
        )
        cls.stage_order_1 = cls.FSMStage.create(
            {
                "name": "Order Stage 1",
                "stage_type": "order",
                "action_id": cls.server_action_order.id,
                "sequence": 14,
            }
        )
        cls.stage_order_2 = cls.FSMStage.create(
            {
                "name": "Order Stage 2",
                "stage_type": "order",
                "action_id": cls.server_action_order.id,
                "sequence": 15,
            }
        )
        # Worker
        cls.field = cls.env["ir.model.fields"]._get(cls.FSMPerson._name, "phone")
        cls.server_action_worker = cls.ServerAction.create(
            {
                "name": "Worker Server Action",
                "model_id": cls.env["ir.model"]._get_id("fsm.person"),
                "crud_model_id": cls.env["ir.model"]._get_id("fsm.person"),
                "value": cls.phone,
                "update_path": "phone",
                "update_field_id": cls.env["ir.model.fields"]._get_ids("fsm.person")[
                    "phone"
                ],
                "evaluation_type": "value",
                "state": "object_write",
            }
        )
        cls.stage_worker_1 = cls.FSMStage.create(
            {
                "name": "Worker Stage 1",
                "stage_type": "worker",
                "action_id": cls.server_action_worker.id,
                "sequence": 16,
            }
        )
        cls.stage_worker_2 = cls.FSMStage.create(
            {
                "name": "Worker Stage 2",
                "stage_type": "worker",
                "action_id": cls.server_action_worker.id,
                "sequence": 17,
            }
        )

    def test_fsm_equipment(self):
        # Create
        self.equipment = self.FSMEquipment.create(
            {"name": "Equipment", "stage_id": self.stage_equipment_1.id}
        )
        self.assertEqual(len(self.equipment.activity_ids), 1)
        # Write
        self.equipment.write({"stage_id": self.stage_equipment_2.id})
        self.assertEqual(len(self.equipment.activity_ids), 2)

    def test_fsm_location(self):
        # Create
        self.worker = self.FSMPerson.create({"name": "Worker"})
        self.location = self.FSMLocation.create(
            {
                "name": "Location",
                "stage_id": self.stage_location_1.id,
                "owner_id": self.worker.id,
            }
        )
        self.assertEqual(len(self.location.activity_ids), 1)
        # Write
        self.location.write({"stage_id": self.stage_location_2.id})
        self.assertEqual(len(self.location.activity_ids), 2)

    def test_fsm_order(self):
        # Create
        self.worker = self.FSMPerson.create({"name": "Worker"})
        self.location = self.FSMLocation.create(
            {"name": "Location", "owner_id": self.worker.id}
        )
        self.order = self.FSMOrders.create(
            {
                "name": "Order",
                "stage_id": self.stage_order_1.id,
                "location_id": self.location.id,
            }
        )
        self.assertEqual(len(self.order.activity_ids), 1)
        # Write
        self.order.write({"stage_id": self.stage_order_2.id})
        self.assertEqual(len(self.order.activity_ids), 2)

    def test_fsm_worker(self):
        self.worker = self.FSMPerson.create(
            {"name": "Worker", "stage_id": self.stage_worker_1.id}
        )
        self.assertEqual(self.worker.phone, self.phone)
        self.worker.write({"phone": False})
        self.worker.write({"stage_id": self.stage_worker_2.id})
        self.assertEqual(self.worker.phone, self.phone)

    def test_fsm_order_run_action(self):
        test_location = self.env.ref("fieldservice.test_location")
        stage1 = self.env.ref("fieldservice.fsm_stage_completed")
        stage2 = self.env.ref("fieldservice.fsm_stage_cancelled")
        create_action = self.env["ir.actions.server"].create(
            {
                "model_id": self.env["ir.model"]._get_id("fsm.tag"),
                "crud_model_id": self.env["ir.model"]._get_id("fsm.tag"),
                "name": "Create new tag",
                "value": "New test tag",
                "state": "object_create",
            }
        )
        stage2.action_id = create_action
        order = self.FSMOrders.create(
            {
                "location_id": test_location.id,
                "stage_id": stage1.id,
            }
        )
        self.assertFalse(self.FSMTag.search([("name", "=", "New test tag")]).exists())
        with RecordCapturer(self.FSMTag, []) as capture:
            order.write({"stage_id": stage2.id})
        tag = capture.records
        self.assertEqual(1, len(tag))
        self.assertEqual("New test tag", tag.name)
