# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMOrder(models.Model):
    _name = 'fsm.order'
    _description = 'Field Service Order'

    def _default_stage_id(self):
        return self.env.ref('fieldservice.fsm_stage_new')

    name = fields.Char(string='Name', required=True)
    fsm_route_id = fields.Many2one('fsm.route', string='Route')
    customer_id = fields.Many2one('res.partner', string='Customer',
                                  domain=('customer', '=', True))
    fsm_location_id = fields.Many2one('fsm.location', string='Location')
    fsm_person_id = fields.Many2one('fsm.person',
                                    string='Field Service Person')
    requested_date = fields.Datetime(string='Requested Date')
    scheduled_date = fields.Datetime(string='Scheduled Date')
    date = fields.Datetime(string='Date')
    description = fields.Text(string='Description')
    stage_id = fields.Many2one('fsm.stage', string='Stage',
                               track_visibility='onchange',
                               index=True,
                               default=lambda self: self._default_stage_id())
