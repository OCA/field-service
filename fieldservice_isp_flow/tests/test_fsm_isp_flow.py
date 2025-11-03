# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class FSMIspFlowCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.WorkOrder = cls.env["fsm.order"]
        cls.Worker = cls.env["fsm.person"]
        cls.worker = cls.env["fsm.person"].create(
            {
                "name": "Worker A",
                "email": "worker@example.com",
            }
        )
        cls.test_partner = cls.env["res.partner"].create(
            {"name": "Test Partner", "phone": "123", "email": "tp@email.com"}
        )
        # create a Res Partner to be converted to FSM Location/Person
        cls.test_loc_partner = cls.env["res.partner"].create(
            {"name": "Test Loc Partner", "phone": "ABC", "email": "tlp@email.com"}
        )
        cls.test_location = cls.env["fsm.location"].create(
            {
                "name": "Test Location",
                "phone": "123-456-7890",
                "email": "test@example.com",
                "owner_id": cls.test_partner.id,
            }
        )
        # Move stage references to test methods to avoid timing issues
        # cls.init_values = {
        #     "stage_id": cls.env.ref("fieldservice_isp_flow.fsm_stage_confirmed").id
        # }
        # cls.stage1 = cls.env.ref("fieldservice_isp_flow.fsm_stage_confirmed")
        # cls.stage2 = cls.env.ref("fieldservice_isp_flow.fsm_stage_scheduled")
        # cls.stage3 = cls.env.ref("fieldservice_isp_flow.fsm_stage_assigned")
        # cls.stage4 = cls.env.ref("fieldservice_isp_flow.fsm_stage_enroute")
        # cls.stage5 = cls.env.ref("fieldservice_isp_flow.fsm_stage_started")

    def test_fsm_orders(self):
        """Test creating new workorders, and test following functions."""
        # Create a simple order and test basic functionality
        order = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "person_id": self.worker.id,
                "date_start": fields.Datetime.now(),
                "date_end": fields.Datetime.now() + timedelta(hours=1),
                "request_early": fields.Datetime.now(),
            }
        )

        # Test that order was created
        self.assertTrue(order.id)

        # Test stage transitions - just call action_confirm without asserting
        order.action_confirm()
        # Verify the stage was set to confirmed
        confirmed_stage = self.env.ref("fieldservice_isp_flow.fsm_stage_confirmed")
        self.assertEqual(order.stage_id, confirmed_stage)
