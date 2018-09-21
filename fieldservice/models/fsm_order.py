# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMOrder(models.Model):
    _name = 'fsm.order'
    _description = 'Field Service Order'

    name = fields.Char(string='Name', required=True)
    fsm_route_id = fields.Many2one('fsm.route', string='Route')
    partner_id = fields.Many2one('res.partner', string='Customer',
                                 domain=('customer', '=', True))
    fsm_location_id = fields.Many2one('fsm.location', string='Location')
    fsm_person_id = fields.Many2one('fsm.person', string='Field Service Person')
    requested_date = fields.Datetime(string='Requested Date')
    scheduled_date = fields.Datetime(string='Scheduled Date')
    date = fields.Datetime(string='Date')
    description = fields.Char(string='Description')
    fsm_stage_id = fields.Many2one('fsm.stage', string='Stage')
