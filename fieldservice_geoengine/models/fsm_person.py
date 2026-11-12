# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMPerson(models.Model):
    _inherit = "fsm.person"

    preferred_route_id = fields.Many2one("fsm.route", string="Preferred Route")
    shape = fields.GeoPoint("Coordinate", compute="_compute_shape", store=True)
    stage_name = fields.Char(related="stage_id.name", string="Stage Name")
    custom_color = fields.Char(related="stage_id.custom_color", string="Stage Color")

    @api.model_create_multi
    def create(self, vals_list):
        persons = super().create(vals_list)
        not_localized = persons.filtered(
            lambda person: not person.partner_latitude or not person.partner_longitude
        )
        if not_localized:
            not_localized.with_context(force_geo_localize=True).geo_localize()
        return persons

    def geo_localize(self):
        self.mapped("partner_id").geo_localize()

    @api.depends("partner_latitude", "partner_longitude")
    def _compute_shape(self):
        for person in self:
            if person.partner_latitude or person.partner_longitude:
                person.shape = fields.GeoPoint.from_latlon(
                    cr=person.env.cr,
                    latitude=person.partner_latitude,
                    longitude=person.partner_longitude,
                )
            else:
                person.shape = False
