# Copyright (C) 2018 Open Source Integrators
# Copyright (C) 2023 - TODAY Pytech SRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMLocation(models.Model):
    _inherit = "fsm.location"

    # Geometry Field
    shape = fields.GeoPoint("Coordinate", compute="_compute_shape", store=True)
    shape_kind = fields.Selection(
        [("point", "Point"), ("area", "Area")],
        string="Geometry",
        default="point",
        required=True,
    )
    area_shape = fields.GeoPolygon(string="Area")
    stage_name = fields.Char(related="stage_id.name", string="Stage Name")
    custom_color = fields.Char(related="stage_id.custom_color", string="Stage Color")

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        not_localized_locations = res.filtered(
            lambda location: not location.partner_latitude
            or not location.partner_longitude
        )
        if not_localized_locations:
            not_localized_locations.with_context(force_geo_localize=True).geo_localize()
        res._sync_route_from_areas()
        return res

    def write(self, vals):
        res = super().write(vals)
        if {"partner_latitude", "partner_longitude", "shape"} & set(vals):
            self._sync_route_from_areas()
        return res

    def geo_localize(self):
        self.mapped("partner_id").geo_localize()
        self._sync_route_from_areas()

    def _sync_route_from_areas(self):
        """Assign each location to a route whose area contains its point."""
        if self.env.context.get("skip_route_area_sync"):
            return
        routes = self.env["fsm.route"].search([("area_shape", "!=", False)])
        for location in self:
            containing = self.env["fsm.route"]
            if location.shape:
                for route in routes:
                    if self.search_count(
                        [
                            ("id", "=", location.id),
                            ("shape", "geo_intersect", route.area_shape),
                        ]
                    ):
                        containing |= route
            if location.fsm_route_id in containing:
                continue
            if containing:
                chosen = min(containing, key=lambda route: route.area_shape.area)
                location.with_context(skip_route_area_sync=True).write(
                    {"fsm_route_id": chosen.id}
                )
            elif location.fsm_route_id.area_shape:
                location.with_context(skip_route_area_sync=True).write(
                    {"fsm_route_id": False}
                )

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
