# Copyright (C) 2019 - TODAY, Brian McMaster, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.rrule import rruleset

from odoo import fields, models


class FSMFrequencySet(models.Model):
    _name = 'fsm.frequency.set'
    _description = 'Frequency Rule Set for Field Service Orders'
    _inherit = ['mail.thread']

    name = fields.Char('Name', required=True)
    active = fields.Boolean(default=True)
    fsm_frequency_ids = fields.Many2many(
        'fsm.frequency', track_visibility='onchange',
        string='Frequency Rules')
    schedule_days = fields.Integer(
        string='Days Ahead to Schedule', default='30',
        help="""The number of days from today that the scheduler will generate
            orders for this rule""", track_visibility='onchange')
    buffer_early = fields.Integer(
        string='Early Buffer', track_visibility='onchange',
        help="""The allowed number of days before the computed schedule date
            that an event can be done""")
    buffer_late = fields.Integer(
        string='Late Buffer', track_visibility='onchange',
        help="""The allowed number of days after the computed schedule date
           that an event can be done""")

    def _get_rruleset(self, dtstart=None, until=None):
        self.ensure_one()
        rset = rruleset()
        for rule in self.fsm_frequency_ids:
            if not rule.is_exclusive:
                rset.rrule(rule._get_rrule(dtstart, until))
            else:
                rset.exrule(rule._get_rrule(dtstart))
        return rset
