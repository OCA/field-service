# Copyright (C) 2019, Patrick Wilson
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Lead(models.Model):
    _inherit = "crm.lead"

    fsm_order_ids = fields.One2many(
        "fsm.order", "opportunity_id", string="Service Orders"
    )
    fsm_location_id = fields.Many2one(
        "fsm.location",
        string="FSM Location",
        domain="[('partner_id', '=', partner_id)]"
    )
    fsm_order_count = fields.Integer(
        compute="_compute_fsm_order_count", string="# FSM Orders"
    )
    # Territory fields
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
    # Geolocation fields
    partner_latitude = fields.Float(
        string="Latitude",
        digits=(8, 6)
    )
    partner_longitude = fields.Float(
        string="Longitude",
        digits=(8, 6)
    )

    def _compute_fsm_order_count(self):
        for rec in self:
            rec.fsm_order_count = len(rec.fsm_order_ids)

    def write(self, vals):
        res = super().write(vals)
        geo_fields = {'partner_latitude', 'partner_longitude', 'district_id', 'fsm_location_id'}
        if geo_fields & set(vals):
            for rec in self:
                if rec.fsm_location_id and rec.fsm_location_id.partner_id:
                    loc_partner = rec.fsm_location_id.partner_id
                    loc_vals = {}
                    if 'partner_latitude' in vals and rec.partner_latitude:
                        loc_vals['partner_latitude'] = rec.partner_latitude
                    if 'partner_longitude' in vals and rec.partner_longitude:
                        loc_vals['partner_longitude'] = rec.partner_longitude
                    if 'district_id' in vals and rec.district_id:
                        loc_vals['district_id'] = rec.district_id.id
                    if loc_vals:
                        loc_partner.write(loc_vals)
        return res
