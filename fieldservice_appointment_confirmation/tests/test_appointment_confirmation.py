# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError

from .common import FieldServiceAppointmentCommon


class TestAppointmentConfirmation(FieldServiceAppointmentCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stage_closed = cls.env["fsm.stage"].create(
            {
                "name": "Done (test)",
                "stage_type": "order",
                "sequence": 9002,
                "is_closed": True,
            }
        )

    def test_prerequisites_button(self):
        self.assertTrue(self.order.can_request_confirmation)
        self.order.person_id = False
        self.assertFalse(self.order.can_request_confirmation)
        self.order.person_id = self.person
        self.location.email = False
        self.assertFalse(self.order.can_request_confirmation)

    def test_request_without_prerequisites_raises(self):
        self.order.person_id = False
        self.assertFalse(self.order.can_request_confirmation)
        with self.assertRaises(UserError):
            self.order.action_request_appointment_confirmation()

    def test_state_label(self):
        self.assertEqual(self.order.appointment_state_label, "Pending")
        self.order.appointment_state = "requested"
        self.assertEqual(self.order.appointment_state_label, "Requested")
        self.order.appointment_state = "confirmed"
        self.assertEqual(self.order.appointment_state_label, "Confirmed")

    def test_state_label_after_reschedule(self):
        self.order.write(
            {"appointment_state": "confirmed", "appointment_reschedule_count": 1}
        )
        self.assertEqual(self.order.appointment_state_label, "Confirmed (rescheduled)")

    def test_calendar_label(self):
        self.assertEqual(self.order.appointment_calendar_label, self.order.name)
        self.order.appointment_state = "confirmed"
        self.assertEqual(self.order.appointment_calendar_label, f"✅ {self.order.name}")

    def test_calendar_label_manual_write(self):
        self.order.appointment_calendar_label = "Manual label"
        self.assertEqual(self.order.appointment_calendar_label, "Manual label")

    def test_access_url(self):
        self.assertEqual(
            self.order.access_url,
            f"/fieldservice/appointment/{self.order.id}/confirm",
        )

    def test_request_regenerates_token(self):
        self.order.action_request_appointment_confirmation()
        first = self.order.access_token
        self.assertTrue(first)
        self.order.action_request_appointment_confirmation()
        second = self.order.access_token
        self.assertTrue(second)
        self.assertNotEqual(first, second)

    def test_mark_requested(self):
        self.order._mark_appointment_requested()
        self.assertEqual(self.order.appointment_state, "requested")

    def test_wizard_send_marks_requested(self):
        action = self.order.action_request_appointment_confirmation()
        self.assertEqual(self.order.appointment_state, "pending")
        ctx = action["context"]
        wizard = (
            self.env["fsm.appointment.confirmation.wizard"]
            .with_context(**ctx)
            .create({})
        )
        wizard.action_send_mail()
        self.order.invalidate_recordset()
        self.assertEqual(self.order.appointment_state, "requested")

    def test_confirm_appointment(self):
        self.order.confirm_appointment(confirmed_by="John Customer")
        self.assertEqual(self.order.appointment_state, "confirmed")
        self.assertTrue(self.order.appointment_confirmed_date)
        self.assertEqual(self.order.appointment_confirmed_by, "John Customer")
        messages = self.order.message_ids.mapped("body")
        self.assertTrue(any("confirmed" in (m or "").lower() for m in messages))

    def test_token_access_rejected_on_closed_stage(self):
        self.order._regenerate_appointment_token()
        token = self.order.access_token
        self.assertTrue(self.order._check_appointment_access(token))
        self.order.stage_id = self.stage_closed
        self.assertFalse(self.order._check_appointment_access(token))

    def test_token_access_rejected_on_wrong_token(self):
        self.order._regenerate_appointment_token()
        self.assertFalse(self.order._check_appointment_access("wrong-token"))

    def test_token_access_rejected_without_token(self):
        self.order._regenerate_appointment_token()
        self.assertFalse(self.order._check_appointment_access(False))

    def test_token_access_rejected_when_order_has_no_token(self):
        order = self._create_order(self.start)
        self.assertFalse(order.access_token)
        self.assertFalse(order._check_appointment_access("any-token"))

    def test_confirm_appointment_without_mail_template(self):
        self.env.ref(
            "fieldservice_appointment_confirmation."
            "mail_template_appointment_confirmed"
        ).unlink()
        self.order.confirm_appointment(confirmed_by="No template")
        self.assertEqual(self.order.appointment_state, "confirmed")

    def test_ics_generation(self):
        content = self.order._get_appointment_ics()
        self.assertIn("BEGIN:VCALENDAR", content)
        self.assertIn("BEGIN:VEVENT", content)
        self.assertIn("DTSTART:", content)
        self.assertIn("DTEND:", content)
        self.assertIn("SUMMARY:", content)
