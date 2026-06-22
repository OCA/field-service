# Copyright (C) 2019, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from freezegun import freeze_time

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class TestFSMActivity(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Order = self.env["fsm.order"]
        self.test_location = self.env.ref("fieldservice.test_location")
        self.Activity = self.env["fsm.activity"]
        self.template_obj = self.env["fsm.template"]
        self.activty_type = self.env["mail.activity.type"].create(
            {"name": "Meeting", "category": "phonecall"}
        )
        self.user_employee = self.env["res.users"].create(
            {
                "name": "Ernest Employee",
                "login": "emp",
                "email": "e.e@example.com",
                "signature": "--\nErnest",
                "notification_type": "inbox",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.env.ref("base.group_user").id,
                            self.env.ref("base.group_partner_manager").id,
                        ],
                    )
                ],
            }
        )

    @freeze_time("2025-03-19")
    def test_fsm_activity(self):
        """Test creating new activites, and moving them along thier stages,
        - Don't move FSM Order to complete if Required Activity in 'To Do'
        - Check completed_by is saved
        - Check completed_on is saved
        """
        # Create an Orders
        view_id = "fieldservice.fsm_order_form"
        with Form(self.Order, view=view_id) as f:
            f.location_id = self.test_location
        order = f.save()
        order2 = self.Order.create(
            {
                "location_id": self.test_location.id,
            }
        )
        order_id = order.id
        self.Activity.create(
            self.get_activity_vals("Activity Test", False, "Ref 1", order2.id)
        )
        self.Activity.create(
            self.get_activity_vals("Activity 1", False, "Ref 1", order_id)
        )
        self.Activity.create(
            self.get_activity_vals("Activity 2", False, "Ref 2", order_id)
        )
        self.Activity.create(
            self.get_activity_vals("Activity 3", True, "Ref 3", order_id)
        )
        order2.order_activity_ids.action_done()
        order2.action_complete()
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

        # As per FSM order needs, end date may not be set
        # stop tracking validation error
        if not order.date_end:
            order.date_end = datetime.now()

        # Test required Activity
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

    def test_compute_order_activity_ids(self):
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
        # Test FSM Order has FSM Activity based on the FSM Template
        self.assertEqual(
            len(self.fso.order_activity_ids),
            len(self.fso.template_id.temp_activity_ids),
            "Amount of FSM Activites on FSM Order should be the same as FSM Template",
        )
        self.assertEqual(
            self.fso.order_activity_ids[0].name,
            self.fso.template_id.temp_activity_ids[0].name,
            "Name of FSM Activity on FSM Order should match FSM Template",
        )
        self.assertEqual(
            self.fso.order_activity_ids[0].required,
            self.fso.template_id.temp_activity_ids[0].required,
            "Required field of FSM Activity on FSM Order should match FSM Template",
        )
        self.assertEqual(
            self.fso.order_activity_ids[0].ref,
            self.fso.template_id.temp_activity_ids[0].ref,
            "Reference of FSM Activity on FSM Order should match FSM Template",
        )
