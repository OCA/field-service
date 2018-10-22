# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytz

from odoo import api, fields, models


class FSMLocation(models.Model):
    _name = 'fsm.location'
    _description = 'Field Service Location'

    @api.model
    def _tz_get(self):
        return [(tz, tz) for tz in sorted(pytz.all_timezones,
                                          key=lambda tz: tz
                                          if not tz.startswith('Etc/')
                                          else '_')]

    direction = fields.Char(string='Directions')
    partner_id = fields.Many2one('res.partner', string='Related Partner',
                                 required=True, ondelete='restrict',
                                 delegate=True, auto_join=True)
    owner_id = fields.Many2one('res.partner', string='Related Owner',
                               required=True, ondelete='restrict',
                               auto_join=True)
    customer_id = fields.Many2one('res.partner', string='Related Customer',
                                  required=True, ondelete='restrict',
                                  auto_join=True)
    tag_ids = fields.Many2many('fsm.tag',
                               string='Tags')
    description = fields.Char(string='Description')
    location_id = fields.Many2one('location', string='Location')
    territory_id = fields.Many2one('territory', string='Territory')
    branch_id = fields.Many2one('branch', string='Branch')
    district_id = fields.Many2one('district', string='District')
    region_id = fields.Many2one('region', string='Region')
    timezone = fields.Selection(_tz_get, string='Timezone')

    @api.model
    def create(self, vals):
        vals.update({'fsm_location': True})
        return super(FSMLocation, self).create(vals)

    @api.onchange('territory_id')
    def _onchange_territory_id(self):
        self.branch_id = self.territory_id.branch_id

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        self.district_id = self.branch_id.district_id

    @api.onchange('district_id')
    def _onchange_district_id(self):
        self.region_id = self.district_id.region_id
