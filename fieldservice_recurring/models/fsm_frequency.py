# Copyright (C) 2019 - TODAY, Brian McMaster, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMFrequency(models.Model):
    _name = 'fsm.frequency'
    _description = 'Frequency for Field Service Orders'
    _inherit = ['mail.thread']

    name = fields.Char('Name', required=True)
    active = fields.Boolean(default=True)
    interval = fields.Integer(
        string='Day Interval', help="The number of days between events",
        default=1, track_visibility='onchange')
    buffer_early = fields.Integer(
        string='Early Buffer', track_visiblity='onchange',
        help="""The allowed number of days before the computed schedule date
            that an event can be done""")
    buffer_late = fields.Integer(
        string='Late Buffer', track_visiblity='onchange',
        help="""The allowed number of days after the computed schedule date
           that an event can be done""")
