# Copyright (C) 2018 Open Source Integrators
# Copyright (C) 2023 - TODAY Pytech SRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMLocation(models.Model):
    _inherit = "fsm.location"

    # Geometry Field
    shape = fields.GeoPoint("Coordinate", compute="_compute_shape", store=True)
    stage_name = fields.Char(related="stage_id.name", string="Stage Name")
    custom_color = fields.Char(related="stage_id.custom_color", string="Stage Color")

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        if not res.partner_latitude or not res.partner_longitude:
            res.with_context(force_geo_localize=True).geo_localize()
        return res

    def geo_localize(self):
        self.mapped("partner_id").geo_localize()

    @api.depends("partner_latitude", "partner_longitude")
    def _compute_shape(self):
        for loc in self:
            if loc.partner_latitude or loc.partner_longitude:
                point = fields.GeoPoint.from_latlon(
                    cr=loc.env.cr,
                    latitude=loc.partner_latitude,
                    longitude=loc.partner_longitude,
                )
                loc.shape = point
            else:
                loc.shape = False
