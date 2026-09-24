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


class FSMDeliveryTimeRange(models.Model):
    _name = "fsm.delivery.time.range"
    _description = "Delivery Time Range"
    _order = "sequence, start_time asc"

    name = fields.Char(compute="_compute_name", store=True)
    start_time = fields.Float(required=True, help="Start hour (e.g. 8.0 for 08:00)")
    end_time = fields.Float(required=True, help="End hour (e.g. 14.0 for 14:00)")
    sequence = fields.Integer(
        default=10,
        help="Customize the order of time ranges. Lower numbers are shown first.",
    )

    # Seasonal recurring validity fields (without year)
    is_seasonal = fields.Boolean(
        compute="_compute_is_seasonal",
        store=True,
        help=(
            "If checked, this schedule overrides the default schedule during "
            "the specified dates."
        ),
    )
    month_start = fields.Selection(MONTH_SELECTION, string="Start Month")
    day_start = fields.Integer(string="Start Day", default=1)
    month_end = fields.Selection(MONTH_SELECTION, string="End Month")
    day_end = fields.Integer(string="End Day", default=1)

    @api.depends(
        "start_time",
        "end_time",
        "is_seasonal",
        "month_start",
        "day_start",
        "month_end",
        "day_end",
    )
    def _compute_name(self):
        for record in self:
            start_str = "{:02d}:{:02d}".format(*divmod(int(record.start_time * 60), 60))
            end_str = "{:02d}:{:02d}".format(*divmod(int(record.end_time * 60), 60))
            base_name = f"{start_str} - {end_str}"
            if record.is_seasonal:
                base_name += (
                    f" ({record.day_start}/{record.month_start} - "
                    f"{record.day_end}/{record.month_end})"
                )
            record.name = base_name

    @api.depends("month_start", "day_start", "month_end", "day_end")
    def _compute_is_seasonal(self):
        for record in self:
            record.is_seasonal = bool(
                record.month_start
                and record.day_start
                and record.month_end
                and record.day_end
            )

    @api.constrains("start_time", "end_time")
    def _check_time_range(self):
        for record in self:
            if record.start_time >= record.end_time:
                raise ValidationError(
                    _("The start time must be earlier than the end time.")
                )

    @api.constrains("month_start", "day_start", "month_end", "day_end")
    def _check_seasonal_completeness(self):
        for record in self:
            has_start = bool(record.month_start and record.day_start)
            has_end = bool(record.month_end and record.day_end)
            has_any = bool(record.month_start or record.month_end)

            if has_any and not (has_start and has_end):
                raise ValidationError(
                    _(
                        "Both start date (month & day) and end date (month & day) "
                        "must be provided for a seasonal schedule."
                    )
                )

    def _validate_day_for_month(self, month_val, day_val, label):
        if not month_val:
            return
        month_dict = dict(self._fields["month_start"]._description_selection(self.env))
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

    @api.constrains("day_start", "month_start", "day_end", "month_end")
    def _check_days(self):
        for record in self:
            record._validate_day_for_month(
                record.month_start, record.day_start, _("Start day")
            )
            record._validate_day_for_month(
                record.month_end, record.day_end, _("End day")
            )

    def is_active_on_date(self, target_date):
        """Evaluates recurring (month, day) period against target_date."""
        self.ensure_one()
        if not self.is_seasonal:
            return True

        target_tuple = (target_date.month, target_date.day)
        start_tuple = (int(self.month_start), self.day_start)
        end_tuple = (int(self.month_end), self.day_end)

        if start_tuple <= end_tuple:
            return start_tuple <= target_tuple <= end_tuple
        else:
            return target_tuple >= start_tuple or target_tuple <= end_tuple
