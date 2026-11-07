# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import calendar

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

MONTH_SELECTION = [
    ("1", "January"),
    ("2", "February"),
    ("3", "March"),
    ("4", "April"),
    ("5", "May"),
    ("6", "June"),
    ("7", "July"),
    ("8", "August"),
    ("9", "September"),
    ("10", "October"),
    ("11", "November"),
    ("12", "December"),
]

LEAP_YEAR_REF = 2024


def is_active_seasonal_date(target_date, month_start, day_start, month_end, day_end):
    """Evaluates if a target date falls inside a recurring month/day period."""
    if not (month_start and day_start and month_end and day_end):
        return False
    target_tuple = (target_date.month, target_date.day)
    start_tuple = (int(month_start), day_start)
    end_tuple = (int(month_end), day_end)

    if start_tuple <= end_tuple:
        return start_tuple <= target_tuple <= end_tuple
    else:
        return target_tuple >= start_tuple or target_tuple <= end_tuple


class FSMDeliveryScheduleLineMixin(models.AbstractModel):
    _name = "fsm.delivery.schedule.line.mixin"
    _description = "FSM Delivery Schedule Line Mixin"
    _order = "day_of_week, start_time"

    is_seasonal = fields.Boolean(default=False)
    day_of_week = fields.Selection(
        [
            ("0", "Monday"),
            ("1", "Tuesday"),
            ("2", "Wednesday"),
            ("3", "Thursday"),
            ("4", "Friday"),
            ("5", "Saturday"),
            ("6", "Sunday"),
        ],
        string="Day of Week",
        required=True,
    )
    start_time = fields.Float(required=True)
    end_time = fields.Float(required=True)

    @api.constrains("start_time", "end_time")
    def _check_time_range(self):
        for record in self:
            if not (0.0 <= record.start_time < 24.0) or not (
                0.0 <= record.end_time < 24.0
            ):
                raise ValidationError(_("Hours must be between 00:00 and 23:59."))
            if record.start_time >= record.end_time:
                raise ValidationError(
                    _("The start time must be earlier than the end time.")
                )

    @api.constrains("day_of_week")
    def _check_day_of_week_allowed(self):
        day_names = list(calendar.day_name)
        for line in self:
            parent = getattr(line, "location_id", False) or getattr(
                line, "route_id", False
            )
            if parent:
                allowed_days = parent.get_allowed_route_days()
                if allowed_days:
                    allowed_indices = [
                        str(day_names.index(d.name))
                        for d in allowed_days
                        if d.name in day_names
                    ]
                    if line.day_of_week not in allowed_indices:
                        day_label = dict(
                            line._fields["day_of_week"]._description_selection(self.env)
                        ).get(line.day_of_week)
                        raise ValidationError(
                            _(
                                "Cannot set a schedule for %(day)s because it is not "
                                "listed in the operational delivery days for this "
                                "location/route."
                            )
                            % {"day": day_label}
                        )


class FSMDeliveryScheduleMixin(models.AbstractModel):
    _name = "fsm.delivery.schedule.mixin"
    _description = "FSM Delivery Schedule Mixin"

    has_default_schedule = fields.Boolean(
        string="Has custom default schedule",
        default=False,
    )
    default_start_time = fields.Float(
        help="Default delivery start hour (00:00 - 23:59)"
    )
    default_end_time = fields.Float(help="Default delivery end hour (00:00 - 23:59)")
    has_day_schedule = fields.Boolean(
        string="Differentiate schedule by day of week",
        default=False,
    )
    has_seasonal_schedule = fields.Boolean(
        string="Has seasonal schedule",
        default=False,
    )
    seasonal_month_start = fields.Selection(MONTH_SELECTION, string="Start Month")
    seasonal_day_start = fields.Integer(string="Start Day", default=1)
    seasonal_month_end = fields.Selection(MONTH_SELECTION, string="End Month")
    seasonal_day_end = fields.Integer(string="End Day", default=1)

    seasonal_start_time = fields.Float()
    seasonal_end_time = fields.Float()
    has_seasonal_day_schedule = fields.Boolean(
        string="Differentiate seasonal schedule by day",
        default=False,
    )

    @api.constrains("has_default_schedule", "default_start_time", "default_end_time")
    def _check_default_time(self):
        for rec in self:
            if rec.has_default_schedule:
                if not (0.0 <= rec.default_start_time < 24.0) or not (
                    0.0 <= rec.default_end_time < 24.0
                ):
                    raise ValidationError(
                        _("Default hours must be between 00:00 and 23:59.")
                    )
                if rec.default_start_time >= rec.default_end_time:
                    raise ValidationError(
                        _("Default start time must be earlier than end time.")
                    )

    @api.constrains("has_seasonal_schedule", "seasonal_start_time", "seasonal_end_time")
    def _check_seasonal_time(self):
        for rec in self:
            if rec.has_seasonal_schedule:
                if not (0.0 <= rec.seasonal_start_time < 24.0) or not (
                    0.0 <= rec.seasonal_end_time < 24.0
                ):
                    raise ValidationError(
                        _("Seasonal hours must be between 00:00 and 23:59.")
                    )
                if rec.seasonal_start_time >= rec.seasonal_end_time:
                    raise ValidationError(
                        _("Seasonal start time must be earlier than end time.")
                    )

    def _validate_day_for_month(self, month_val, day_val, label):
        if not month_val:
            return
        month_dict = dict(
            self._fields["seasonal_month_start"]._description_selection(self.env)
        )
        month_name = month_dict.get(month_val)
        max_days = calendar.monthrange(LEAP_YEAR_REF, int(month_val))[1]
        if not (1 <= day_val <= max_days):
            raise ValidationError(
                _(
                    "%(label)s for %(month)s must be between 1 and "
                    "%(max_days)s. Got %(day)s."
                )
                % {
                    "label": label,
                    "month": month_name,
                    "max_days": max_days,
                    "day": day_val,
                }
            )

    @api.constrains(
        "has_seasonal_schedule",
        "seasonal_day_start",
        "seasonal_month_start",
        "seasonal_day_end",
        "seasonal_month_end",
    )
    def _check_seasonal_days(self):
        for record in self:
            if record.has_seasonal_schedule:
                if not (
                    record.seasonal_month_start
                    and record.seasonal_day_start
                    and record.seasonal_month_end
                    and record.seasonal_day_end
                ):
                    raise ValidationError(
                        _(
                            "Both start and end month/day must be provided for a "
                            "seasonal schedule."
                        )
                    )
                record._validate_day_for_month(
                    record.seasonal_month_start,
                    record.seasonal_day_start,
                    _("Start day"),
                )
                record._validate_day_for_month(
                    record.seasonal_month_end, record.seasonal_day_end, _("End day")
                )

    def get_allowed_route_days(self):
        """Override in inheriting models to return allowed fsm.route.day recordset."""
        self.ensure_one()
        return self.env.company.fsm_default_route_day_ids or self.env[
            "fsm.route.day"
        ].search([])

    def _resolve_delivery_hours(self, target_date):
        self.ensure_one()
        day_str = str(target_date.weekday())

        # 1. Seasonal Schedule Check
        if (
            self.has_seasonal_schedule
            and self.seasonal_month_start
            and self.seasonal_day_start
            and self.seasonal_month_end
            and self.seasonal_day_end
        ):
            if is_active_seasonal_date(
                target_date,
                self.seasonal_month_start,
                self.seasonal_day_start,
                self.seasonal_month_end,
                self.seasonal_day_end,
            ):
                if self.has_seasonal_day_schedule:
                    day_line = self.seasonal_schedule_line_ids.filtered(
                        lambda line: line.day_of_week == day_str
                    )
                    if day_line:
                        return day_line[0].start_time, day_line[0].end_time

                if self.seasonal_start_time < self.seasonal_end_time:
                    return self.seasonal_start_time, self.seasonal_end_time

        # 2. Default Schedule Check
        if self.has_default_schedule:
            if self.has_day_schedule:
                day_line = self.default_schedule_line_ids.filtered(
                    lambda line: line.day_of_week == day_str
                )
                if day_line:
                    return day_line[0].start_time, day_line[0].end_time

            if self.default_start_time < self.default_end_time:
                return self.default_start_time, self.default_end_time

        return None
