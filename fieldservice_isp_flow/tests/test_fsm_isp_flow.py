# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class FSMIspFlowCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.WorkOrder = cls.env["fsm.order"]
        cls.Worker = cls.env["fsm.person"]
        view_id = "fieldservice.fsm_person_form"
        with Form(cls.Worker, view=view_id) as f:
            f.name = "Worker A"
        cls.worker = f.save()
        cls.test_partner = cls.env["res.partner"].create(
            {"name": "Test Partner", "phone": "123", "email": "tp@email.com"}
        )
        # create a Res Partner to be converted to FSM Location/Person
        cls.test_loc_partner = cls.env["res.partner"].create(
            {"name": "Test Loc Partner", "phone": "ABC", "email": "tlp@email.com"}
        )
        cls.test_location = cls.env.ref("fieldservice.test_location")
        cls.init_values = {
            "stage_id": cls.env.ref("fieldservice_isp_flow.fsm_stage_confirmed").id
        }
        cls.stage1 = cls.env.ref("fieldservice_isp_flow.fsm_stage_confirmed")
        cls.stage2 = cls.env.ref("fieldservice_isp_flow.fsm_stage_scheduled")
        cls.stage3 = cls.env.ref("fieldservice_isp_flow.fsm_stage_assigned")
        cls.stage4 = cls.env.ref("fieldservice_isp_flow.fsm_stage_enroute")
        cls.stage5 = cls.env.ref("fieldservice_isp_flow.fsm_stage_started")

    def test_fsm_orders(self):
        """Test creating new workorders, and test following functions."""
        # Create an Orders
        hours_diff = 100
        date_start = fields.Datetime.today()

        order = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "date_start": date_start,
                "date_end": date_start + timedelta(hours=hours_diff),
                "request_early": fields.Datetime.today(),
            }
        )
        order2 = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "request_early": fields.Datetime.today(),
                "person_id": self.worker.id,
                "date_end": date_start + timedelta(hours=hours_diff),
                "scheduled_date_start": date_start,
            }
        )
        order3 = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "stage_id": self.stage1.id,
            }
        )
        order4 = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "stage_id": self.stage2.id,
            }
        )
        order5 = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "stage_id": self.stage3.id,
            }
        )
        order6 = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "stage_id": self.stage4.id,
            }
        )
        order7 = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "stage_id": self.stage5.id,
            }
        )
        order.action_confirm()
        order.action_enroute()
        order.action_start()
        order2.action_assign()
        order2.action_schedule()
        order3._track_subtype(self.init_values)
        order4._track_subtype(self.init_values)
        order5._track_subtype(self.init_values)
        order6._track_subtype(self.init_values)
        order7._track_subtype(self.init_values)
        order._track_subtype(self.init_values)
        order._track_subtype(self.init_values)
        data_dict = order2.action_schedule()
        self.assertEqual(data_dict, True)
        with self.assertRaises(ValidationError):
            order2.action_complete()
        with self.assertRaises(ValidationError):
            order.action_request()
        with self.assertRaises(ValidationError):
            order.action_assign()
        with self.assertRaises(ValidationError):
            order.action_schedule()
        with self.assertRaises(ValidationError):
            order.date_end = False
            order.action_complete()
        with self.assertRaises(ValidationError):
            order2.action_start()
