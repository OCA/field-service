# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.base_geoengine import fields as geo_fields


class FSMLocation(models.Model):
    _inherit = 'fsm.location'

    # Geometry Field
    shape = fields.GeoPoint('Coordinate')

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
