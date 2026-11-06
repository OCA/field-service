# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime, time, timedelta

from odoo import fields
from odoo.tests import HttpCase, tagged

from .common import FieldServiceAppointmentCommon


@tagged("post_install", "-at_install")
class TestAppointmentPortal(FieldServiceAppointmentCommon, HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order._regenerate_appointment_token()
        cls.token = cls.order.access_token
        # The Sunday before next Monday: outside any working schedule.
        today = fields.Datetime.now().date()
        monday = today + timedelta(days=(7 - today.weekday()) % 7 or 7)
        cls.closed_dt = datetime.combine(monday - timedelta(days=1), time(10, 0))

    def _url(self, action, token=None):
        used_token = token if token is not None else self.token
        return (
            f"/fieldservice/appointment/{self.order.id}/{action}"
            f"?access_token={used_token}"
        )

    def test_confirm_get_then_post(self):
        resp = self.url_open(self._url("confirm"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.order.name, resp.text)
        self.assertEqual(self.order.appointment_state, "pending")
        resp = self.url_open(
            self._url("confirm"),
            data={"access_token": self.token, "confirmed_by": "Web Tester"},
        )
        self.assertEqual(resp.status_code, 200)
        self.order.invalidate_recordset()
        self.assertEqual(self.order.appointment_state, "confirmed")
        self.assertEqual(self.order.appointment_confirmed_by, "Web Tester")

    def test_invalid_token_rejected(self):
        resp = self.url_open(self._url("confirm", token="bad-token"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("no longer available", resp.text)
        self.assertEqual(self.order.appointment_state, "pending")

    def test_invalid_token_rejected_on_every_route(self):
        bad = "bad-token"
        for resp in (
            self.url_open(self._url("reschedule", token=bad)),
            self.url_open(self._url("ics", token=bad)),
            self.url_open(self._url("confirm", token=bad), data={"access_token": bad}),
            self.url_open(
                self._url("reschedule", token=bad), data={"access_token": bad}
            ),
        ):
            self.assertEqual(resp.status_code, 200)
            self.assertIn("no longer available", resp.text)
        self.order.invalidate_recordset()
        self.assertEqual(self.order.appointment_state, "pending")

    def test_reschedule_post_without_slot_redirects(self):
        resp = self.url_open(
            self._url("reschedule"),
            data={"access_token": self.token},
            allow_redirects=False,
        )
        self.assertIn(resp.status_code, (302, 303))
        self.assertIn("/reschedule", resp.headers.get("Location", ""))

    def test_reschedule_post_unavailable_slot_shows_error(self):
        resp = self.url_open(
            self._url("reschedule"),
            data={
                "access_token": self.token,
                "slot": self.closed_dt.strftime("%Y-%m-%d %H:%M:%S"),
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("The selected slot is no longer available", resp.text)
        self.order.invalidate_recordset()
        self.assertNotEqual(self.order.appointment_state, "confirmed")
        self.assertEqual(self.order.appointment_reschedule_count, 0)

    def test_ics_download(self):
        resp = self.url_open(self._url("ics"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/calendar", resp.headers.get("Content-Type", ""))
        self.assertIn("BEGIN:VCALENDAR", resp.text)
        self.assertIn("BEGIN:VEVENT", resp.text)

    def test_reschedule_get_then_post(self):
        resp = self.url_open(self._url("reschedule"))
        self.assertEqual(resp.status_code, 200)
        now = fields.Datetime.now()
        slots = self.order._get_worker_available_slots(now, now + timedelta(days=14))
        self.assertTrue(slots, "Expected at least one available slot in 14 days")
        chosen = slots[0].strftime("%Y-%m-%d %H:%M:%S")
        resp = self.url_open(
            self._url("reschedule"),
            data={"access_token": self.token, "slot": chosen},
        )
        self.assertEqual(resp.status_code, 200)
        self.order.invalidate_recordset()
        self.assertEqual(self.order.appointment_state, "confirmed")
        self.assertEqual(self.order.appointment_reschedule_count, 1)

    def test_past_appointment_redirects_to_reschedule(self):
        self.order.write(
            {
                "scheduled_date_start": fields.Datetime.now() - timedelta(days=1),
                "appointment_state": "requested",
            }
        )
        resp = self.url_open(self._url("confirm"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Reschedule your appointment", resp.text)
        self.url_open(
            self._url("confirm"),
            data={"access_token": self.token, "confirmed_by": "Late customer"},
        )
        self.order.invalidate_recordset()
        self.assertNotEqual(self.order.appointment_state, "confirmed")
