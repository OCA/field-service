# Copyright (C) 2019, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class TestFSMActivity(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Order = self.env["fsm.order"]
        self.test_location = self.env.ref("fieldservice.test_location")
        self.Activity = self.env["fsm.activity"]
        self.template_obj = self.env["fsm.template"]

    def test_fsm_activity(self):
        """ Test creating new activites, and moving them along thier stages,
            - Don't move FSM Order to complete if Required Activity in 'To Do'
            - Check completed_by is saved
            - Check completed_on is saved
        """
        # Create an Orders
        view_id = "fieldservice.fsm_order_form"
        with Form(self.Order, view=view_id) as f:
            f.location_id = self.test_location
        order = f.save()
        order_id = order.id
        self.Activity.create(
            self.get_activity_vals("Activity 1", False, "Ref 1", order_id)
        )
        self.Activity.create(
            self.get_activity_vals("Activity 2", False, "Ref 2", order_id)
        )
        self.Activity.create(
            self.get_activity_vals("Activity 3", True, "Ref 3", order_id)
        )
        # Test action_done()
        order.order_activity_ids[0].action_done()
        self.assertEqual(
            order.order_activity_ids[0].completed_on.replace(microsecond=0),
            datetime.now().replace(microsecond=0),
        )
        self.assertEqual(order.order_activity_ids[0].completed_by, self.env.user)
        self.assertEqual(order.order_activity_ids[0].state, "done")
        # Test action_cancel()
        order.order_activity_ids[1].action_cancel()
        self.assertEqual(order.order_activity_ids[1].state, "cancel")

        # Test Reqired Activity
        with self.assertRaises(ValidationError):
            order.action_complete()

        order.order_activity_ids[2].action_done()
        order.action_complete()
        self.assertEqual(
            order.stage_id.id, self.env.ref("fieldservice.fsm_stage_completed").id
        )

    def get_activity_vals(self, name, required, ref, order_id):
        return {
            "name": name,
            "required": required,
            "ref": ref,
            "fsm_order_id": order_id,
        }

    def test_onchange_template_id(self):
        # Create a Template
        self.template = self.template_obj.create(
            {
                "name": "Demo template",
                "temp_activity_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Activity new",
                            "required": True,
                            "ref": "Ref new",
                            "state": "todo",
                        },
                    )
                ],
            }
        )
        # Create an Order
        self.fso = self.Order.create(
            {"location_id": self.test_location.id, "template_id": self.template.id}
        )
        # Test _onchange_template_id()
        self.fso._onchange_template_id()
        self.assertNotEquals(
            self.fso.order_activity_ids.ids, self.fso.template_id.temp_activity_ids.ids
        )
