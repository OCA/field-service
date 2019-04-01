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

    ref = fields.Char(string='Internal Reference', copy=False)
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

    fsm_parent_id = fields.Many2one('fsm.location', string='Parent')
    notes = fields.Text(string="Notes")
    person_ids = fields.Many2many('fsm.person',
                                  'fsm_person_location_rel',
                                  'fsm_location_id',
                                  'fsm_person_id',
                                  string='Preferred Workers')
    contact_count = fields.Integer(string='Contacts',
                                   compute='_compute_contact_ids')
    equipment_count = fields.Integer(string='Equipment',
                                     compute='_compute_equipment_ids')
    sublocation_count = fields.Integer(string='Sub Locations',
                                       compute='_compute_sublocation_ids')
    complete_name = fields.Char(string='Complete Name',
                                compute='_compute_complete_name',
                                stored='_compute_complete_name')
    stage_id = fields.Many2one('fsm.stage', string='Stage',
                               track_visibility='onchange',
                               index=True, copy=False,
                               group_expand='_read_group_stage_ids',
                               default=lambda self: self._default_stage_id())
    hide = fields.Boolean(default=False)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.user.company_id)

    @api.depends('name', 'fsm_parent_id.complete_name')
    def _compute_complete_name(self):
        for loc in self:
            if loc.fsm_parent_id:
                loc.complete_name = '%s / %s' % (
                    loc.fsm_parent_id.complete_name, loc.name)
            else:
                loc.complete_name = loc.name

    @api.multi
    def name_get(self):
        results = []
        for rec in self:
            results.append((rec.id, rec.complete_name))
        return results

    # Geometry Field
    shape = geo_fields.GeoPoint(string='Coordinate')

    _sql_constraints = [('fsm_location_ref_uniq', 'unique (ref)',
                         'This internal reference already exists!')]

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['fsm.stage'].search([('stage_type',
                                                   '=', 'location')])
        return stage_ids

    def _default_stage_id(self):
        return self.env['fsm.stage'].search([('stage_type', '=', 'location'),
                                             ('sequence', '=', '1')])

    def advance_stage(self):
        seq = self.stage_id.sequence
        next_stage = self.env['fsm.stage'].search(
            [('stage_type', '=', 'location'), ('sequence', '=', seq+1)])
        self.stage_id = next_stage
        self._onchange_stage_id()

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        # get last stage
        heighest_stage = self.env['fsm.stage'].search(
            [('stage_type', '=', 'location')],
            order='sequence desc',
            limit=1)
        if self.stage_id.name == heighest_stage.name:
            self.hide = True
        else:
            self.hide = False

    @api.model
    def create(self, vals):
        vals.update({'fsm_location': True})
        res = super(FSMLocation, self).create(vals)
        lat = self.partner_id.partner_latitude
        lng = self.partner_id.partner_longitude
        if lat == 0.0 and lng == 0.0:
            res.geo_localize()
        else:
            point = geo_fields.GeoPoint.from_latlon(cr=self.env.cr,
                                                    latitude=lat,
                                                    longitude=lng)
            self.shape = point
        return res

    @api.onchange('fsm_parent_id')
    def _onchange_fsm_parent_id(self):
        self.owner_id = self.fsm_parent_id.owner_id or False
        self.customer_id = self.fsm_parent_id.customer_id or False
        self.contact_id = self.fsm_parent_id.contact_id or False
        self.direction = self.fsm_parent_id.direction or False
        self.street = self.fsm_parent_id.street or False
        self.street2 = self.fsm_parent_id.street2 or False
        self.city = self.fsm_parent_id.city or False
        self.zip = self.fsm_parent_id.zip or False
        self.state_id = self.fsm_parent_id.state_id or False
        self.country_id = self.fsm_parent_id.country_id or False
        self.timezone = self.fsm_parent_id.timezone or False
        self.territory_id = self.fsm_parent_id.territory_id or False

    @api.onchange('territory_id')
    def _onchange_territory_id(self):
        self.territory_manager_id = self.territory_id.person_id or False
        self.person_ids = self.territory_id.person_ids or False
        self.branch_id = self.territory_id.branch_id or False

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        self.branch_manager_id = \
            self.territory_id.branch_id.partner_id or False
        self.district_id = self.branch_id.district_id or False

    @api.onchange('district_id')
    def _onchange_district_id(self):
        self.district_manager_id = \
            self.branch_id.district_id.partner_id or False
        self.region_id = self.district_id.region_id or False

    @api.onchange('region_id')
    def _onchange_region_id(self):
        self.region_manager_id = self.region_id.partner_id or False

    def comp_count(self, contact, equipment, loc):
        if equipment:
            for child in loc:
                child_locs = self.env['fsm.location'].\
                    search([('fsm_parent_id', '=', child.id)])
                equip = self.env['fsm.equipment'].\
                    search_count([('location_id',
                                 '=', child.id)])
            if child_locs:
                for loc in child_locs:
                    equip += loc.comp_count(0, 1, loc)
            return equip
        elif contact:
            for child in loc:
                child_locs = self.env['fsm.location'].\
                    search([('fsm_parent_id', '=', child.id)])
                con = self.env['res.partner'].\
                    search_count([('service_location_id',
                                 '=', child.id)])
            if child_locs:
                for loc in child_locs:
                    con += loc.comp_count(1, 0, loc)
            return con
        else:
            for child in loc:
                child_locs = self.env['fsm.location'].\
                    search([('fsm_parent_id', '=', child.id)])
                subloc = self.env['fsm.location'].\
                    search_count([('fsm_parent_id', '=', child.id)])
            if child_locs:
                for loc in child_locs:
                    subloc += loc.comp_count(0, 0, loc)
            return subloc

    def get_action_views(self, contact, equipment, loc):
        if equipment:
            for child in loc:
                child_locs = self.env['fsm.location'].\
                    search([('fsm_parent_id', '=', child.id)])
                equip = self.env['fsm.equipment'].\
                    search([('location_id', '=', child.id)])
            if child_locs:
                for loc in child_locs:
                    equip += loc.get_action_views(0, 1, loc)
            return equip
        elif contact:
            for child in loc:
                child_locs = self.env['fsm.location'].\
                    search([('fsm_parent_id', '=', child.id)])
                con = self.env['res.partner'].\
                    search([('service_location_id', '=', child.id)])
            if child_locs:
                for loc in child_locs:
                    con += loc.get_action_views(1, 0, loc)
            return con
        else:
            for child in loc:
                child_locs = self.env['fsm.location'].\
                    search([('fsm_parent_id', '=', child.id)])
                subloc = child_locs
            if child_locs:
                for loc in child_locs:
                    subloc += loc.get_action_views(0, 0, loc)
            return subloc

    @api.multi
    def action_view_contacts(self):
        '''
        This function returns an action that display existing contacts
        of given fsm location id and its child locations. It can
        either be a in a list or in a form view, if there is only one
        contact to show.
        '''
        for location in self:
            action = self.env.ref('contacts.action_contacts').\
                read()[0]
            contacts = self.get_action_views(1, 0, location)
            if len(contacts) > 1:
                action['domain'] = [('id', 'in', contacts.ids)]
            elif contacts:
                action['views'] = [(self.env.ref('base.view_partner_form').id,
                                    'form')]
                action['res_id'] = contacts.id
            return action

    @api.multi
    def _compute_contact_ids(self):
        for loc in self:
            contacts = self.comp_count(1, 0, loc)
            loc.contact_count = contacts

    @api.multi
    def action_view_equipment(self):
        '''
        This function returns an action that display existing
        equipment of given fsm location id. It can either be a in
        a list or in a form view, if there is only one equipment to show.
        '''
        for location in self:
            action = self.env.ref('fieldservice.action_fsm_equipment').\
                read()[0]
            equipment = self.get_action_views(0, 1, location)
            if len(equipment) == 0 or len(equipment) > 1:
                action['domain'] = [('id', 'in', equipment.ids)]
            elif equipment:
                action['views'] = [(self.env.
                                    ref('fieldservice.' +
                                        'fsm_equipment_form_view').id,
                                    'form')]
                action['res_id'] = equipment.id
            return action

    @api.multi
    def _compute_sublocation_ids(self):
        for loc in self:
            sublocation = self.comp_count(0, 0, loc)
            loc.sublocation_count = sublocation

    @api.multi
    def action_view_sublocation(self):
        '''
        This function returns an action that display existing
        sub-locations of a given fsm location id. It can either be a in
        a list or in a form view, if there is only one sub-location to show.
        '''
        for location in self:
            action = self.env.ref('fieldservice.action_fsm_location').read()[0]
            sublocation = self.get_action_views(0, 0, location)
            if len(sublocation) > 1 or len(sublocation) == 0:
                action['domain'] = [('id', 'in', sublocation.ids)]
            elif sublocation:
                action['views'] = [(self.env.
                                    ref('fieldservice.' +
                                        'fsm_location_form_view').id,
                                    'form')]
                action['res_id'] = sublocation.id
            return action

    @api.multi
    def _compute_equipment_ids(self):
        for loc in self:
            equipment = self.comp_count(0, 1, loc)
            loc.equipment_count = equipment
        for location in self:
            child_locs = self.env['fsm.location']. \
                search([('fsm_parent_id', '=', location.id)])
            equipment = (self.env['fsm.equipment'].
                         search_count([('location_id',
                                        'in', child_locs.ids)]) +
                         self.env['fsm.equipment'].
                         search_count([('location_id',
                                        '=', location.id)]))
            location.equipment_count = equipment or 0

    def geo_localize(self):
        for loc in self:
            if loc.partner_id:
                loc.partner_id.geo_localize()
            lat = loc.partner_latitude
            lng = loc.partner_longitude
            point = geo_fields.GeoPoint.from_latlon(cr=loc.env.cr,
                                                    latitude=lat,
                                                    longitude=lng)
            loc.shape = point

    def _update_order_geometries(self):
        for loc in self:
            orders = loc.env['fsm.order'].search(
                [('location_id', '=', loc.id)])
            for order in orders:
                order.create_geometry()

    @api.multi
    def write(self, vals):
        res = super(FSMLocation, self).write(vals)
        if ('partner_latitude' in vals) and ('partner_longitude' in vals):
            self.shape = geo_fields.GeoPoint.from_latlon(
                cr=self.env.cr,
                latitude=vals['partner_latitude'],
                longitude=vals['partner_longitude'])
            self._update_order_geometries()
        return res
