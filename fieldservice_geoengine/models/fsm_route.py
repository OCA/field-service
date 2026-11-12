# Copyright (C) 2026 Gray Matter Logic
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMRoute(models.Model):
    _name = "fsm.route"
    _inherit = ["fsm.route", "mail.thread", "mail.activity.mixin"]

    area_shape = fields.GeoPolygon(string="Area")
    location_ids = fields.One2many(
        comodel_name="fsm.location",
        inverse_name="fsm_route_id",
        string="Locations",
    )
    location_count = fields.Integer(compute="_compute_location_count")

    @api.depends("location_ids")
    def _compute_location_count(self):
        for route in self:
            route.location_count = len(route.location_ids)

    def action_view_locations(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Locations"),
            "res_model": "fsm.location",
            "view_mode": "list,form,geoengine",
            "domain": [("fsm_route_id", "=", self.id)],
            "context": {"default_fsm_route_id": self.id},
        }

    @api.model_create_multi
    def create(self, vals_list):
        routes = super().create(vals_list)
        routes.filtered("area_shape")._assign_locations_in_area()
        return routes

    def write(self, vals):
        res = super().write(vals)
        if "area_shape" in vals:
            self._assign_locations_in_area()
        return res

    def _assign_locations_in_area(self):
        """Give this route every location inside its area.

        Locations that leave the area are released, then matched again so
        another route can claim them. The route being saved wins overlaps.
        """
        locations = self.env["fsm.location"]
        for route in self:
            if not route.area_shape:
                released = route.location_ids
                released.write({"fsm_route_id": False})
                released._sync_route_from_areas()
                continue
            inside = locations.search(
                [("shape", "geo_intersect", route.area_shape)]
            )
            current = route.location_ids
            (inside - current).write({"fsm_route_id": route.id})
            released = current - inside
            released.write({"fsm_route_id": False})
            released._sync_route_from_areas()
