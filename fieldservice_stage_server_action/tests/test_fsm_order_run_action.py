# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import RecordCapturer, TransactionCase


class TestFSMOrderRunAction(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Order = cls.env["fsm.order"]
        cls.Tag = cls.env["fsm.tag"]
        cls.test_location = cls.env.ref("fieldservice.test_location")
        cls.stage1 = cls.env.ref("fieldservice.fsm_stage_completed")
        cls.stage2 = cls.env.ref("fieldservice.fsm_stage_cancelled")
        cls.location_1 = cls.env.ref("fieldservice.location_1")
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

    def test_fsm_order_run_action(self):
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
