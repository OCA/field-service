# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    district_id = fields.Many2one("res.district", string="District")
    region_id = fields.Many2one(
        "res.region", string="Region",
        compute="_compute_region_id", store=True, readonly=False)
    state_id = fields.Many2one(
        "res.country.state", string="State",
        compute="_compute_state_id", store=True, readonly=False)
    country_id = fields.Many2one(
        "res.country", string="Country",
        compute="_compute_country_id", store=True, readonly=False)

    @api.depends('district_id')
    def _compute_region_id(self):
        for rec in self:
            rec.region_id = rec.district_id.region_id if rec.district_id else False

    @api.depends('region_id')
    def _compute_state_id(self):
        for rec in self:
            rec.state_id = rec.region_id.state_id if rec.region_id else False

    @api.depends('state_id')
    def _compute_country_id(self):
        for rec in self:
            rec.country_id = rec.state_id.country_id if rec.state_id else False

    @api.onchange('region_id')
    def _onchange_region_id(self):
        domain = {}
        if self.region_id:
            domain['district_id'] = [('region_id', '=', self.region_id.id)]
        else:
            domain['district_id'] = []
        return {'domain': domain}

    @api.onchange('state_id')
    def _onchange_state_id(self):
        domain = {}
        if self.state_id:
            domain['region_id'] = [('state_id', '=', self.state_id.id)]
        else:
            domain['region_id'] = []
        return {'domain': domain}

    @api.onchange('country_id')
    def _onchange_country_id(self):
        domain = {}
        if self.country_id:
            domain['state_id'] = [('country_id', '=', self.country_id.id)]
        else:
            domain['state_id'] = []
        return {'domain': domain}

    @api.model
    def _resolve_district_from_coordinates(self, lat, lng):
        """Find district containing (lat, lng) via point-in-polygon."""
        return self.env['res.district'].find_by_coordinates(lat, lng)

    @api.model
    def _resolve_district_from_address(self, street, city=False):
        """Try to extract district name from address string."""
        if not street:
            return False
        text = f"{street} {city or ''}"
        districts = self.env['res.district'].search([])
        for d in districts:
            if d.name in text:
                return d
        return False

    @api.model
    def _auto_resolve_district(self, vals):
        """Set district_id from lat/lng or address."""
        lat = vals.get('partner_latitude')
        lng = vals.get('partner_longitude')
        district = False
        if lat and lng:
            district = self._resolve_district_from_coordinates(lat, lng)
        if not district:
            district = self._resolve_district_from_address(
                vals.get('street', ''),
                vals.get('city', ''),
            )
        if district:
            vals['district_id'] = district.id
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._auto_resolve_district(vals)
        return super().create(vals_list)

    def write(self, vals):
        if any(f in vals for f in ('partner_latitude', 'partner_longitude', 'street')):
            for record in self:
                rec_vals = dict(vals)
                if 'partner_latitude' not in rec_vals:
                    rec_vals['partner_latitude'] = record.partner_latitude
                if 'partner_longitude' not in rec_vals:
                    rec_vals['partner_longitude'] = record.partner_longitude
                if 'street' not in rec_vals:
                    rec_vals['street'] = record.street
                self._auto_resolve_district(rec_vals)
                super(ResPartner, record).write(rec_vals)
            return True
        return super().write(vals)
