import pytz

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    def _compute_utc_date(self, date):
        if date:
            date = pytz.utc.localize(date)
            return date.astimezone(pytz.timezone(self.env.user.tz or "UTC"))

    def _check_worker_availability(self, scheduled_date, scheduled_date_end, person_id):
        person = self.env["fsm.person"].browse(person_id)
        calendar = person.calendar_id
        scheduled_date_dt = fields.Datetime.from_string(scheduled_date)
        scheduled_date_dt_utc = self._compute_utc_date(scheduled_date_dt)
        scheduled_date_end_dt = fields.Datetime.from_string(scheduled_date_end)
        scheduled_date_end_dt_utc = self._compute_utc_date(scheduled_date_end_dt)

        employee = self.env["hr.employee"].search(
            [("work_contact_id", "=", person.partner_id.id)], limit=1
        )
        if employee and employee.resource_id:
            overlapping_leave = self.env["resource.calendar.leaves"].search(
                [
                    ("resource_id", "=", employee.resource_id.id),
                    ("date_from", "<=", scheduled_date_end_dt),
                    ("date_to", ">=", scheduled_date_dt),
                ]
            )

            if overlapping_leave:
                date_from = overlapping_leave.date_from
                date_from_utc = self._compute_utc_date(date_from)
                date_to = overlapping_leave.date_to
                date_to_utc = self._compute_utc_date(date_to)
                raise ValidationError(
                    _(
                        "%(name)s has a registered leave from "
                        "%(leave_start)s to %(leave_end)s, "
                        "which overlaps with the scheduled time of this order "
                        "(from %(order_start)s to %(order_end)s).\nReason: %(reason)s"
                    )
                    % {
                        "name": person.name,
                        "leave_start": date_from_utc.strftime("%Y-%m-%d %H:%M"),
                        "leave_end": date_to_utc.strftime("%Y-%m-%d %H:%M"),
                        "order_start": scheduled_date_dt_utc.strftime("%Y-%m-%d %H:%M"),
                        "order_end": scheduled_date_end_dt_utc.strftime(
                            "%Y-%m-%d %H:%M"
                        ),
                        "reason": overlapping_leave.name,
                    }
                )

        if calendar:
            weekday = scheduled_date_dt_utc.strftime("%A")
            float_hour_start = (
                scheduled_date_dt_utc.hour + scheduled_date_dt_utc.minute / 60.0
            )
            float_hour_end = (
                scheduled_date_end_dt_utc.hour + scheduled_date_end_dt_utc.minute / 60.0
            )

            matched = False
            for att in calendar.attendance_ids:
                day_label = dict(att._fields["dayofweek"].selection).get(att.dayofweek)
                if (
                    day_label == weekday
                    and att.hour_from <= float_hour_start
                    and float_hour_end <= att.hour_to
                    and att.day_period != "lunch"
                ):
                    matched = True
                    break

            if not matched:
                raise ValidationError(
                    _(
                        "%(name)s is not scheduled to work at "
                        "the selected time range %(date)s / %(date_end)s."
                    )
                    % {
                        "name": person.name,
                        "date": scheduled_date_dt_utc.strftime("%Y-%m-%d %H:%M"),
                        "date_end": scheduled_date_end_dt_utc.strftime(
                            "%Y-%m-%d %H:%M"
                        ),
                    }
                )

    @api.constrains("scheduled_date_start", "scheduled_date_end", "person_id")
    def check_worker_availability(self):
        for order in self:
            if order.scheduled_date_start and order.person_id:
                self._check_worker_availability(
                    order.scheduled_date_start,
                    order.scheduled_date_end,
                    order.person_id.id,
                )
