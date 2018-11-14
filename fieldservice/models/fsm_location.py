# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytz

from odoo import api, fields, models


class FSMLocation(models.Model):
    _name = 'fsm.location'
    _inherits = {'res.partner': 'partner_id'}
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
    customer_id = fields.Many2one('res.partner', string='Billed Customer',
                                  required=True, ondelete='restrict',
                                  auto_join=True)
    contact_id = fields.Many2one('res.partner', string='Primary Contact',
                                 ondelete='restrict', auto_join=True)
    tag_ids = fields.Many2many('fsm.tag', string='Tags')
    description = fields.Char(string='Description')
    territory_id = fields.Many2one('fsm.territory', string='Territory')
    branch_id = fields.Many2one('fsm.branch', string='Branch')
    district_id = fields.Many2one('fsm.district', string='District')
    region_id = fields.Many2one('fsm.region', string='Region')
    person_id = fields.Many2one(string='Primary Assignment',
                                related='territory_id.person_id')
    district_manager_id = fields.Many2one(string='District Manager',
                                          related='district_id.partner_id')
    region_manager_id = fields.Many2one(string='Region Manager',
                                        related='region_id.partner_id')
    branch_manager_id = fields.Many2one(string='Branch Manager',
                                        related='branch_id.partner_id')

    timezone = fields.Selection(_tz_get, string='Timezone')

    parent_id = fields.Many2one('fsm.location', string='Parent')
    notes = fields.Text(string="Notes")
    person_ids = fields.Many2many('fsm.person', 'partner_id',
                                  string='Preferred Workers')

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
