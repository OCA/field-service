# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResDistrict(models.Model):
    _name = "res.district"
    _description = "District"

    name = fields.Char(required=True, translate=True)
    region_id = fields.Many2one("res.region", string="Region")
    partner_id = fields.Many2one("res.partner", string="District Manager")
    description = fields.Char()
    polygon_ids = fields.One2many(
        "res.district.polygon.point", "district_id", string="Polygon Points"
    )

    @api.model
    def find_by_coordinates(self, lat, lng):
        """Return the district whose polygon contains (lat, lng) using ray casting, or False."""
        if not lat or not lng:
            return False
        lat = float(lat)
        lng = float(lng)
        districts = self.search([('polygon_ids', '!=', False)])
        for district in districts:
            pts = district.polygon_ids.sorted('sequence')
            if len(pts) < 3:
                continue
            poly = [(p.lat, p.lng) for p in pts]
            if self._point_in_polygon(lat, lng, poly):
                return district
        return False

    @api.model
    def _point_in_polygon(self, lat, lng, poly):
        """Ray casting. poly = [(vertex_lat, vertex_lng)]. Returns True if point is inside."""
        inside = False
        n = len(poly)
        j = n - 1
        for i in range(n):
            y_i, x_i = poly[i]
            y_j, x_j = poly[j]
            if ((y_i > lat) != (y_j > lat)) and \
               (lng < (x_j - x_i) * (lat - y_i) / (y_j - y_i) + x_i):
                inside = not inside
            j = i
        return inside
