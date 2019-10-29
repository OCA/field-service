# Copyright (C) 2019 - TODAY, Brian McMaster, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.rrule import MO, TU, WE, TH, FR, SA, SU
from dateutil.rrule import YEARLY, MONTHLY, WEEKLY, DAILY
from dateutil.rrule import rrule

from odoo import fields, models, api, _
from odoo.exceptions import UserError


WEEKDAYS = {
    'mo': MO,
    'tu': TU,
    'we': WE,
    'th': TH,
    'fr': FR,
    'sa': SA,
    'su': SU
}

FREQUENCIES = {
    'yearly': YEARLY,
    'monthly': MONTHLY,
    'weekly': WEEKLY,
    'daily': DAILY,
}

FREQUENCY_SELECT = [
    ('yearly', 'Yearly'),
    ('monthly', 'Monthly'),
    ('weekly', 'Weekly'),
    ('daily', 'Daily')
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
    _name = 'fsm.frequency'
    _description = 'Frequency Rule for Field Service Orders'
    _inherit = ['mail.thread']

    name = fields.Char('Name', required=True)
    active = fields.Boolean(default=True)
    interval = fields.Integer(
        string='Repeat Every', help="The number of intervals between events",
        default=1, required=True, track_visibility='onchange')
    interval_type = fields.Selection(
        FREQUENCY_SELECT, string='Interval Type',
        required=True, track_visibility='onchange')
    is_exclusive = fields.Boolean(
        string='Exclusive Rule?', default=False,
        help="""Checking this box will make this an exclusive rule. Exclusive
            rules prevent the configured days from being a schedule option""")
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.user.company_id)
    use_bymonthday = fields.Boolean(
        string='Use Day of Month',
        help="""When selected you will be able to specify which calendar day
            of the month the event occurs on""")
    month_day = fields.Integer(
        string='Day of Month', track_visibility='onchange')

    use_byweekday = fields.Boolean(
        string='Use Days of Week',
        help="""When selected you will be able to choose which days of the
            week the scheduler will include (or exclude if Exclusive rule)""")
    mo = fields.Boolean('Monday', default=False)
    tu = fields.Boolean('Tuesday', default=False)
    we = fields.Boolean('Wednesday', default=False)
    th = fields.Boolean('Thursday', default=False)
    fr = fields.Boolean('Friday', default=False)
    sa = fields.Boolean('Saturday', default=False)
    su = fields.Boolean('Sunday', default=False)

    use_bymonth = fields.Boolean(string='Use Months')
    jan = fields.Boolean('January', default=False)
    feb = fields.Boolean('February', default=False)
    mar = fields.Boolean('March', default=False)
    apr = fields.Boolean('April', default=False)
    may = fields.Boolean('May', default=False)
    jun = fields.Boolean('June', default=False)
    jul = fields.Boolean('July', default=False)
    aug = fields.Boolean('August', default=False)
    sep = fields.Boolean('September', default=False)
    oct = fields.Boolean('October', default=False)
    nov = fields.Boolean('November', default=False)
    dec = fields.Boolean('December', default=False)

    use_setpos = fields.Boolean(string='Use Position')
    set_pos = fields.Integer(
        string="By Position",
        help="""Specify an occurrence number, positive or negative,
            corresponding to the nth occurrence of the rule inside
            the frequency period. For example, -1 if combined with a
            'Monthly' frequency, and a weekday of (MO, TU, WE, TH, FR),
            will result in the last work day of every month.""")
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
        if not vals.get('name'):
            hours, minutes = self._split_time_to_hour_min(
                vals.get('planned_hour')
            )
            wd = _(dict(WEEKDAYS_SELECT)[ vals.get('week_day')])
            name = wd + "_" + str(hours) + "_" + str(minutes)
            vals['name'] = name
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

    @api.constrains('set_pos')
    def _check_set_pos(self):
        if self.use_setpos:
            if not (-366 < self.set_pos < 366):
                raise UserError(_("Position must be between -366 and 366"))

    @api.constrains('month_day')
    def _check_month_day(self):
        if self.use_bymonthday:
            if not (1 <= self.month_day <= 31):
                raise UserError(_("'Day of Month must be between 1 and 31"))

    def _get_rrule(self, dtstart=None, until=None):
        self.ensure_one()
        freq = FREQUENCIES[self.interval_type]
        return rrule(freq, interval=self.interval,
                     dtstart=dtstart, until=until,
                     byweekday=self._byweekday(),
                     bymonth=self._bymonth(),
                     bymonthday=self._bymonthday(),
                     bysetpos=self._bysetpos(),
                     )

    def _byweekday(self):
        """
        Checks day of week booleans and builds the value for rrule parameter
        @returns: {list} byweekday: list of WEEKDAY values used for rrule
        """
        self.ensure_one()
        if not self.use_byweekday:
            return None
        weekdays = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
        byweekday = [WEEKDAYS[field] for field in weekdays if self[field]]
        return byweekday

    def _bymonth(self):
        """
        Checks month booleans and builds the value for rrule parameter
        @returns: {list} bymonth: list of integers used for rrule
        """
        self.ensure_one()
        if not self.use_bymonth:
            return None
        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                  'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        bymonth = [months.index(field) + 1 for field in months if self[field]]
        return bymonth

    def _bymonthday(self):
        self.ensure_one()
        if not self.use_bymonthday:
            return None
        return self.month_day

    def _bysetpos(self):
        self.ensure_one()
        if not self.use_setpos or self.set_pos == 0:
            return None
        return self.set_pos
