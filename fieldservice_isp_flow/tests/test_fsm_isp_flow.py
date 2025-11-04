# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
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
        # Create a test team since FSMOrder requires team_id
        cls.test_team = cls.env["fsm.team"].create(
            {
                "name": "Test Team",
            }
        )

    def test_action_confirm(self):
        """Test action_confirm transitions to confirmed stage."""
        order = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "person_id": self.worker.id,
                "team_id": self.test_team.id,
                "date_start": fields.Datetime.now(),
                "date_end": fields.Datetime.now() + timedelta(hours=1),
                "request_early": fields.Datetime.now(),
            }
        )

        order.action_confirm()
        confirmed_stage = self.env.ref("fieldservice_isp_flow.fsm_stage_confirmed")
        self.assertEqual(order.stage_id, confirmed_stage)

    def test_action_request_with_person(self):
        """Test action_request with person_id set."""
        order = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "person_id": self.worker.id,
                "team_id": self.test_team.id,
                "date_start": fields.Datetime.now(),
                "date_end": fields.Datetime.now() + timedelta(hours=1),
                "request_early": fields.Datetime.now(),
            }
        )

        order.action_request()
        requested_stage = self.env.ref("fieldservice_isp_flow.fsm_stage_requested")
        self.assertEqual(order.stage_id, requested_stage)

    def test_action_request_without_person_raises_error(self):
        """Test action_request without person_id raises ValidationError."""
        order = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "team_id": self.test_team.id,
                "date_start": fields.Datetime.now(),
                "date_end": fields.Datetime.now() + timedelta(hours=1),
                "request_early": fields.Datetime.now(),
            }
        )

        with self.assertRaises(ValidationError):
            order.action_request()

    def test_action_assign_with_person(self):
        """Test action_assign with person_id set."""
        order = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "person_id": self.worker.id,
                "team_id": self.test_team.id,
                "date_start": fields.Datetime.now(),
                "date_end": fields.Datetime.now() + timedelta(hours=1),
                "request_early": fields.Datetime.now(),
            }
        )

        order.action_assign()
        assigned_stage = self.env.ref("fieldservice_isp_flow.fsm_stage_assigned")
        self.assertEqual(order.stage_id, assigned_stage)

    def test_action_assign_without_person_raises_error(self):
        """Test action_assign without person_id raises ValidationError."""
        order = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "team_id": self.test_team.id,
                "date_start": fields.Datetime.now(),
                "date_end": fields.Datetime.now() + timedelta(hours=1),
                "request_early": fields.Datetime.now(),
            }
        )

        with self.assertRaises(ValidationError):
            order.action_assign()

    def test_action_schedule_with_required_fields(self):
        """Test action_schedule with person_id and scheduled_date_start."""
        order = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "person_id": self.worker.id,
                "team_id": self.test_team.id,
                "date_start": fields.Datetime.now(),
                "date_end": fields.Datetime.now() + timedelta(hours=1),
                "request_early": fields.Datetime.now(),
                "scheduled_date_start": fields.Datetime.now() + timedelta(hours=2),
            }
        )

        order.action_schedule()
        scheduled_stage = self.env.ref("fieldservice_isp_flow.fsm_stage_scheduled")
        self.assertEqual(order.stage_id, scheduled_stage)

    def test_action_schedule_without_person_raises_error(self):
        """Test action_schedule without person_id raises ValidationError."""
        order = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "team_id": self.test_team.id,
                "date_start": fields.Datetime.now(),
                "date_end": fields.Datetime.now() + timedelta(hours=1),
                "request_early": fields.Datetime.now(),
                "scheduled_date_start": fields.Datetime.now() + timedelta(hours=2),
            }
        )

        with self.assertRaises(ValidationError):
            order.action_schedule()

    def test_action_schedule_without_scheduled_date_raises_error(self):
        """Test action_schedule without scheduled_date_start raises ValidationError."""
        order = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "person_id": self.worker.id,
                "team_id": self.test_team.id,
                "date_start": fields.Datetime.now(),
                "date_end": fields.Datetime.now() + timedelta(hours=1),
                "request_early": fields.Datetime.now(),
            }
        )

        with self.assertRaises(ValidationError):
            order.action_schedule()

    def test_action_enroute(self):
        """Test action_enroute transitions to enroute stage."""
        order = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "person_id": self.worker.id,
                "team_id": self.test_team.id,
                "date_start": fields.Datetime.now(),
                "date_end": fields.Datetime.now() + timedelta(hours=1),
                "request_early": fields.Datetime.now(),
            }
        )

        order.action_enroute()
        enroute_stage = self.env.ref("fieldservice_isp_flow.fsm_stage_enroute")
        self.assertEqual(order.stage_id, enroute_stage)

    def test_action_start_with_date_start(self):
        """Test action_start with date_start set."""
        now = fields.Datetime.now()
        order = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "person_id": self.worker.id,
                "team_id": self.test_team.id,
                "date_start": now,
                "date_end": now + timedelta(hours=1),
                "request_early": now,
            }
        )

        order.action_start()
        started_stage = self.env.ref("fieldservice_isp_flow.fsm_stage_started")
        self.assertEqual(order.stage_id, started_stage)

    def test_action_start_without_date_start_raises_error(self):
        """Test action_start without date_start raises ValidationError."""
        order = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "person_id": self.worker.id,
                "team_id": self.test_team.id,
                "date_end": fields.Datetime.now() + timedelta(hours=1),
                "request_early": fields.Datetime.now(),
            }
        )

        with self.assertRaises(ValidationError):
            order.action_start()

    def test_action_complete_with_date_end_and_resolution(self):
        """Test action_complete with date_end and resolution set."""
        now = fields.Datetime.now()
        order = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "person_id": self.worker.id,
                "team_id": self.test_team.id,
                "date_start": now,
                "date_end": now + timedelta(hours=1),
                "request_early": now,
                "resolution": "Issue resolved",
            }
        )

        result = order.action_complete()
        # action_complete returns the result of super().action_complete()
        self.assertIsNotNone(result)

    def test_action_complete_without_date_end_raises_error(self):
        """Test action_complete without date_end raises ValidationError."""
        order = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "person_id": self.worker.id,
                "team_id": self.test_team.id,
                "date_start": fields.Datetime.now(),
                "request_early": fields.Datetime.now(),
                "resolution": "Issue resolved",
            }
        )

        with self.assertRaises(ValidationError):
            order.action_complete()

    def test_action_complete_without_resolution_raises_error(self):
        """Test action_complete without resolution raises ValidationError."""
        now = fields.Datetime.now()
        order = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "person_id": self.worker.id,
                "team_id": self.test_team.id,
                "date_start": now,
                "date_end": now + timedelta(hours=1),
                "request_early": now,
            }
        )

        with self.assertRaises(ValidationError):
            order.action_complete()

    def test_track_subtype_on_stage_change(self):
        """Test _track_subtype returns correct message type on stage changes."""
        now = fields.Datetime.now()
        order = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "person_id": self.worker.id,
                "team_id": self.test_team.id,
                "date_start": now,
                "date_end": now + timedelta(hours=1),
                "request_early": now,
            }
        )

        # Change to confirmed stage
        order.action_confirm()
        subtype = order._track_subtype({"stage_id": 0})
        # Should return a subtype for confirmed stage
        self.assertIsNotNone(subtype)

    def test_fsm_orders(self):
        """Test creating new workorders, and test following functions."""
        # Create a simple order and test basic functionality
        order = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "person_id": self.worker.id,
                "team_id": self.test_team.id,
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

        # Test action_request - this should work now since person_id is set
        order.action_request()
        requested_stage = self.env.ref("fieldservice_isp_flow.fsm_stage_requested")
        self.assertEqual(order.stage_id, requested_stage)
