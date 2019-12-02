# Copyright (C) 2019 - TODAY, Brian McMaster, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.rrule import (
    DAILY,
    FR,
    MO,
    MONTHLY,
    SA,
    SU,
    TH,
    TU,
    WE,
    WEEKLY,
    YEARLY,
    rrule,
)

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

WEEKDAYS = {"mo": MO, "tu": TU, "we": WE, "th": TH, "fr": FR, "sa": SA, "su": SU}

FREQUENCIES = {"yearly": YEARLY, "monthly": MONTHLY, "weekly": WEEKLY, "daily": DAILY}

FREQUENCY_SELECT = [
    ("yearly", "Yearly"),
    ("monthly", "Monthly"),
    ("weekly", "Weekly"),
    ("daily", "Daily"),
]

WEEKDAYS_SELECT = [
    ("none", "Not defined"),
    ("mo", "MO"),
    ("tu", "TU"),
    ("we", "WE"),
    ("th", "TH"),
    ("fr", "FR"),
    ("sa", "SA"),
    ("su", "SU"),
]

FREQUENCIES = [
    ("1", "First"),
    ("2", "Second"),
    ("3", "Third"),
    ("4", "Forth"),
    ("5", "last"),
    ("6", "Each"),
]


class FSMFrequency(models.Model):
    _inherit = "fsm.frequency"

    use_rrulestr = fields.Boolean(string="Use rrule string")
    rrule_string = fields.Char()
    # simlpe edit helper with planned_hour precision
    interval_frequency = fields.Selection(FREQUENCIES, string="Interval Frequency")
    use_planned_hour = fields.Boolean()
    week_day = fields.Selection(WEEKDAYS_SELECT, string="Week Day")
    planned_hour = fields.Float("Planned Hours")

    @api.onchange("interval_frequency")
    def _onchange_interval_frequency(self):
        """
        Set corresponding interval_type and set_pos
        """
        for freq in self:
            if not freq.interval_frequency:
                freq.use_planned_hour = False
                continue
            freq.interval_type = "monthly"
            freq.use_planned_hour = True
            freq.set_pos = 0
            if freq.interval_frequency == "6":
                freq.interval_type = "weekly"
            elif freq.interval_frequency == "5":
                freq.set_pos = -1
            else:
                freq.set_pos = int(freq.interval_frequency)

    @api.model
    def create(self, vals):
        if not vals.get("name"):
            hours, minutes = self._split_time_to_hour_min(vals.get("planned_hour"))
            wd = _(dict(WEEKDAYS_SELECT)[vals.get("week_day")])
            name = wd + "_" + str(hours) + "_" + str(minutes)
            vals["name"] = name
        return super(FSMFrequency, self).create(vals)

    @api.onchange("week_day")
    def _onchange_week_day(self):
        """
        Checks corresponding day boolean
        """
        for freq in self:
            if freq.week_day and freq.week_day != "none":
                freq.use_byweekday = True
                weekdays = ["mo", "tu", "we", "th", "fr", "sa", "su"]
                # Set all checked weekdays to False and check only Week Day
                for field in weekdays:
                    freq[field] = False
                freq[freq.week_day] = True

    @api.onchange("use_planned_hour")
    def _onchange_use_planned_hour(self):
        """
        Checks use_byweekday boolean
        """
        for freq in self:
            freq.use_byweekday = freq.use_planned_hour

    def _byhours(self):
        self.ensure_one()
        if not self.use_planned_hour or not self.week_day or self.week_day == "none":
            return None
        duration_minute = self.planned_hour * 60
        hours, minutes = self._split_time_to_hour_min(self.planned_hour)
        return hours, minutes

    def _split_time_to_hour_min(self, time):
        if not time:
            time = 0.0
        duration_minute = time * 60
        hours, minutes = divmod(duration_minute, 60)
        return int(hours), int(minutes)

    @api.constrains("week_day", "planned_hour")
    def _check_planned_hour(self):
        if self.week_day == "none" or not self.week_day:
            raise UserError(_("Week day must be set"))
        if self.use_planned_hour:
            hours, minutes = self._byhours()
            if not (0 <= hours <= 23):
                raise UserError(_("Planned hours must be between 0 and 23"))

    def _get_rrule(self, dtstart=None, until=None):
        self.ensure_one()
        import pdb; pdb.set_trace()
        if self.use_planned_hour:

            dtstart = dtstart.replace(hour=0, minute=0, second=0, microsecond=0)
            dtstart = dtstart + relativedelta(hours=+self.planned_hour)

        res = super(FSMFrequency, self)._get_rrule(dtstart=dtstart, until=until)
        return res
