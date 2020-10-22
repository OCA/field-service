# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent consulting Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta
from odoo import fields, models


def daterange(start_date, end_date=None):
    """
    Generator for each date in a period of time
    Optimized for single date special case
    """
    if end_date:
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)
    else:
        yield start_date


class FSMRoute(models.Model):
    _name = 'fsm.route'
    _description = 'Field Service Route'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', required=True)
    territory_id = fields.Many2one('fsm.territory', string='Territory')
    fsm_person_id = fields.Many2one('fsm.person', string='Person')
    day_ids = fields.Many2many('fsm.route.day', string='Days')
    max_order = fields.Integer('Maximum Orders', default=0,
                               help="Maximum number of orders per day route.")
    max_dayroute = fields.Integer(
        'Maximum Routes', default=1,
        help="Maximum number of day routes per day.")

    def run_on(self, check_date):
        """
        Does this Route run on this Day?
        If no run days are set, we consider it does.

        Returns the Day record, or False.
        """
        day_index = check_date.weekday()
        day_rec = self.env.ref(
            'fieldservice_route.fsm_route_day_' + str(day_index))
        route_days = self.mapped('day_ids')
        if route_days and day_rec not in route_days:
            return False
        return day_rec

    def get_scheduled_dates(self, date_from, date_to=False):
        """
        Return a list of scheduled dates for any of the given Routes
        """
        calendar = []
        for day in daterange(date_from, date_to):
            if self.run_on(day):
                calendar.append(day)
        return calendar
