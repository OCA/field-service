# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMLocation(models.Model):
    _name = 'fsm.location'
    _inherits = {'res.partner': 'partner_id'}
    _description = 'Field Service Location'

    direction = fields.Char(string='Directions')
    partner_id = fields.Many2one('res.partner', string='Related Partner',
                                 required=True, ondelete='restrict',
                                 auto_join=True)
    owner_id = fields.Many2one('res.partner', string='Related Owner',
                               required=True, ondelete='restrict',
                               auto_join=True)
    customer_id = fields.Many2one('res.partner', string='Related Customer',
                                  required=True, ondelete='restrict',
                                  auto_join=True)
    tag_ids = fields.Many2many('fsm.tag',
                               string='Tags')
    building = fields.Char(string='Building', size=35)
    floor = fields.Char(string='Floor', size=35)
    unit = fields.Char(string='Unit', size=35)
    room = fields.Char(string='Room', size=35)
    description = fields.Char(string='Description')
    territory = fields.Char(string='Territory', size=35)
    branch = fields.Char(string='Branch', size=35)
    district = fields.Char(string='District', size=35)
    region = fields.Char(string='Region', size=35)
    timezone = fields.Char(string='Timezone', size=35)

    @api.model
    def create(self, vals):
        vals.update({'fsm_location': True})
        return super(FSMLocation, self).create(vals)
