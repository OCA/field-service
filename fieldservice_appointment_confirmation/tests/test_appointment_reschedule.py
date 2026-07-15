# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime, time, timedelta

import pytz
from freezegun import freeze_time

from odoo.exceptions import UserError, ValidationError

from .common import FieldServiceAppointmentCommon


class TestAppointmentReschedule(FieldServiceAppointmentCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        today = datetime.now().date()
        monday = today + timedelta(days=(7 - today.weekday()) % 7 or 7)
        cls.slot_dt = datetime.combine(monday, time(10, 0))
        # The day before that Monday is a Sunday: outside any working schedule.
        cls.closed_dt = datetime.combine(monday - timedelta(days=1), time(10, 0))

    def test_available_slots_exclude_busy(self):
        busy_start = datetime.combine(self.slot_dt.date(), time(11, 0))
        self._create_order(busy_start)
        date_from = datetime.combine(self.slot_dt.date(), time(0, 0))
        date_to = date_from + timedelta(days=1)
        slots = self.order._get_worker_available_slots(date_from, date_to)
        self.assertNotIn(busy_start, slots)

    def test_reschedule_updates_order(self):
        new_start = datetime.combine(self.slot_dt.date(), time(14, 0))
        self.order.reschedule_appointment(new_start)
        self.assertEqual(self.order.scheduled_date_start, new_start)
        self.assertEqual(self.order.appointment_state, "confirmed")
        self.assertEqual(self.order.appointment_reschedule_count, 1)
        self.assertTrue(self.order.appointment_confirmed_date)
        self.assertFalse(self.order.can_request_confirmation)

    def test_reschedule_unavailable_slot_raises(self):
        self.assertFalse(self.order._is_slot_available(self.closed_dt))
        with self.assertRaises(ValidationError):
            self.order.reschedule_appointment(self.closed_dt)

    def test_reschedule_without_mail_template(self):
        self.env.ref(
            "fieldservice_appointment_confirmation."
            "mail_template_appointment_rescheduled"
        ).unlink()
        new_start = datetime.combine(self.slot_dt.date(), time(14, 0))
        self.order.reschedule_appointment(new_start)
        self.assertEqual(self.order.appointment_state, "confirmed")

    def test_slot_duration_param_fallback(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "fieldservice_appointment_confirmation.slot_duration_hours",
            "not-a-number",
        )
        self.assertEqual(self.order._get_slot_duration_hours(), 1.0)

    def test_reschedule_window_param_fallback(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "fieldservice_appointment_confirmation.reschedule_window_days",
            "not-a-number",
        )
        self.assertEqual(self.order._get_reschedule_window_days(), 14)

    def test_unknown_timezone_falls_back_to_utc(self):
        # tz is a Selection field, so an unknown value (e.g. left over from an
        # older pytz database) can only be injected at SQL level.
        self.env.cr.execute(
            "UPDATE res_partner SET tz = %s WHERE id = %s",
            ("Unknown/Timezone", self.customer.id),
        )
        self.customer.invalidate_recordset(["tz"])
        self.assertEqual(self.order._get_appointment_tz(), pytz.UTC)

    def test_without_calendar_there_are_no_slots(self):
        self.person.calendar_id = False
        self.env.company.resource_calendar_id = False
        self.assertFalse(self.order._get_worker_calendar())
        date_from = datetime.combine(self.slot_dt.date(), time(0, 0))
        self.assertEqual(
            self.order._get_worker_available_slots(
                date_from, date_from + timedelta(days=1)
            ),
            [],
        )
        self.assertFalse(self.order._is_slot_available(self.slot_dt))

    @freeze_time("2026-01-12 08:00:00")
    def test_reschedule_past_slot_raises(self):
        self.customer.tz = "UTC"
        past_slot = datetime(2026, 1, 9, 10, 0)
        with self.assertRaises(ValidationError):
            self.order.reschedule_appointment(past_slot)
        self.assertEqual(self.order.appointment_reschedule_count, 0)

    @freeze_time("2026-01-12 08:00:00")
    def test_reschedule_beyond_window_raises(self):
        self.customer.tz = "UTC"
        self.env["ir.config_parameter"].sudo().set_param(
            "fieldservice_appointment_confirmation.reschedule_window_days", "14"
        )
        late_slot = datetime(2026, 2, 2, 10, 0)
        with self.assertRaises(ValidationError):
            self.order.reschedule_appointment(late_slot)
        self.assertEqual(self.order.appointment_reschedule_count, 0)

    @freeze_time("2026-01-12 08:00:00")
    def test_reschedule_inside_window_succeeds(self):
        self.customer.tz = "UTC"
        slot = datetime(2026, 1, 13, 10, 0)
        self.order.reschedule_appointment(slot)
        self.assertEqual(self.order.scheduled_date_start, slot)
        self.assertEqual(self.order.appointment_reschedule_count, 1)

    @freeze_time("2026-01-12 08:00:00")
    def test_reschedule_without_worker_raises(self):
        self.customer.tz = "UTC"
        self.order.person_id = False
        with self.assertRaisesRegex(UserError, "worker"):
            self.order.reschedule_appointment(datetime(2026, 1, 13, 10, 0))
        self.assertEqual(self.order.appointment_reschedule_count, 0)

    @freeze_time("2026-01-12 15:00:00")
    def test_reschedule_window_end_in_customer_timezone(self):
        # Bogota is UTC-5: the 09:00-10:00 local slot on the last day of the
        # window ends exactly when the window does, the 09:30 one goes past it.
        self.customer.tz = "America/Bogota"
        self.env["ir.config_parameter"].sudo().set_param(
            "fieldservice_appointment_confirmation.reschedule_window_days", "14"
        )
        self.assertFalse(self.order._is_slot_available(datetime(2026, 1, 26, 14, 30)))
        self.assertTrue(self.order._is_slot_available(datetime(2026, 1, 26, 14, 0)))

    @freeze_time("2026-01-12 15:00:00")
    def test_every_offered_slot_is_accepted(self):
        self.customer.tz = "America/Bogota"
        now = datetime(2026, 1, 12, 15, 0)
        slots = self.order._get_worker_available_slots(
            now, now + timedelta(days=self.order._get_reschedule_window_days())
        )
        self.assertTrue(slots)
        self.assertTrue(all(self.order._is_slot_available(slot) for slot in slots))
        self.order.reschedule_appointment(slots[-1])
        self.assertEqual(self.order.scheduled_date_start, slots[-1])
