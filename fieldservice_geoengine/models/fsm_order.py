# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    # Geometry Field
    shape = fields.GeoPoint("Coordinate")

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.create_geometry()
        return res

    @api.onchange("location_id")
    def onchange_location_id(self):
        res = super().onchange_location_id()
        if self.location_id:
            self.create_geometry()
        return res

    def create_geometry(self):
        for order in self:
            lat = order.location_id.partner_latitude
            lng = order.location_id.partner_longitude
            point = fields.GeoPoint.from_latlon(
                cr=order.env.cr, latitude=lat, longitude=lng
            )
            order.shape = point

    def geo_localize(self):
        for order in self:
            order.location_id.partner_id.geo_localize()
            order.create_geometry()
