# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime, time, timedelta

import pytz

from odoo.exceptions import ValidationError

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
