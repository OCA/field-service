# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytz

from odoo import api, fields

from odoo.addons.base_geoengine import geo_model
from odoo.addons.base_geoengine import fields as geo_fields


class FSMLocation(geo_model.GeoModel):
    _name = 'fsm.location'
    _inherits = {'res.partner': 'partner_id'}
    _description = 'Field Service Location'

    @api.model
    def _tz_get(self):
        return [(tz, tz) for tz in sorted(pytz.all_timezones,
                                          key=lambda tz: tz
                                          if not tz.startswith('Etc/')
                                          else '_')]

    ref = fields.Char(string='Internal Reference')
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
                                 domain="[('is_company', '=', False),"
                                        " ('fsm_location', '=', False)]",
                                 index=True)
    tag_ids = fields.Many2many('fsm.tag', string='Tags')
    description = fields.Char(string='Description')
    territory_id = fields.Many2one('fsm.territory', string='Territory')
    branch_id = fields.Many2one('fsm.branch', string='Branch')
    district_id = fields.Many2one('fsm.district', string='District')
    region_id = fields.Many2one('fsm.region', string='Region')
    territory_manager_id = fields.Many2one(string='Primary Assignment',
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

    # Geometry Field
    shape = geo_fields.GeoPoint(string='Coordinate')

    _sql_constraints = [('fsm_location_ref_uniq', 'unique (ref)',
                         'This internal reference already exists!')]

    @api.model
    def create(self, vals):
        vals.update({'fsm_location': True})
        return super(FSMLocation, self).create(vals)

    @api.onchange('territory_id')
    def _onchange_territory_id(self):
        if self.territory_id:
            # assign manager
            self.territory_manager_id = self.territory_id.person_id
            # get territory preffered person list if available
            self.person_ids = self.territory_id.person_ids
            if self.territory_id.branch_id:
                self.branch_id = self.territory_id.branch_id
                self.branch_manager_id = self.territory_id.branch_id.partner_id

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        if self.branch_id and self.branch_id.district_id:
            self.district_id = self.branch_id.district_id
            self.district_manager_id = self.branch_id.district_id.partner_id

    @api.onchange('district_id')
    def _onchange_district_id(self):
        if self.district_id and self.district_id.region_id:
            self.region_id = self.district_id.region_id
            self.region_manager_id = self.district_id.region_id.partner_id

    @api.multi
    def name_get(self):
        return [(location.id, '%s%s' % (location.ref and '[%s] ' % location.ref
                                        or '', location.name))
                for location in self]
