# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import RecordCapturer

from odoo.addons.fieldservice.tests.test_fsm_common import FSMCommon


class TestFSMOrderRunAction(FSMCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.Order = cls.env["fsm.order"]
        cls.Tag = cls.env["fsm.tag"]
        cls.stage1 = cls.env.ref("fieldservice.fsm_stage_completed")
        cls.stage2 = cls.env.ref("fieldservice.fsm_stage_cancelled")
        cls.create_action = cls.env["ir.actions.server"].create(
            {
                "model_id": cls.env["ir.model"]._get_id("fsm.tag"),
                "crud_model_id": cls.env["ir.model"]._get_id("fsm.tag"),
                "name": "Create new tag",
                "value": "New test tag",
                "state": "object_create",
            }
        )
        cls.stage2.action_id = cls.create_action

    def test_fsm_order_run_action_on_write(self):
        order = self.Order.create(
            {
                "location_id": self.test_location.id,
                "stage_id": self.stage1.id,
            }
        )
        self.assertFalse(self.Tag.search([("name", "=", "New test tag")]).exists())
        with RecordCapturer(self.Tag, []) as capture:
            order.write({"stage_id": self.stage2.id})
        tag = capture.records
        self.assertEqual(1, len(tag))
        self.assertEqual("New test tag", tag.name)

    def test_fsm_order_run_action_on_create(self):
        with RecordCapturer(self.Tag, []) as capture:
            self.Order.create(
                {
                    "location_id": self.test_location.id,
                    "stage_id": self.stage2.id,
                }
            )
        tag = capture.records
        self.assertEqual(1, len(tag))
        self.assertEqual("New test tag", tag.name)

    def test_fsm_order_run_action_without_action(self):
        stage_without_action = self.env["fsm.stage"].create(
            {
                "name": "Stage Without Action",
                "stage_type": "order",
            }
        )
        stage_without_action_2 = self.env["fsm.stage"].create(
            {
                "name": "Stage Without Action 2",
                "stage_type": "order",
            }
        )
        order = self.Order.create(
            {
                "location_id": self.test_location.id,
                "stage_id": stage_without_action.id,
            }
        )
        order.write({"stage_id": stage_without_action_2.id})

    def test_fsm_order_write_without_stage_change(self):
        order = self.Order.create(
            {
                "location_id": self.test_location.id,
                "stage_id": self.stage1.id,
            }
        )
        order.write({"description": "Updated description"})
