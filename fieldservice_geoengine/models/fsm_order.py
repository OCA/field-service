# Copyright (C) 2018 Open Source Integrators
# Copyright (C) 2023 - TODAY Pytech SRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    shape = fields.GeoPoint(related="location_id.shape", string="Coordinate")
    worker_shape = fields.GeoPoint(
        related="person_id.shape", string="Worker Coordinate"
    )

    def geo_localize(self):
        self.mapped("location_id").geo_localize()

    def get_worker_path(self):
        """Street path from the worker to this order's location."""
        self.ensure_one()
        points = []
        for partner in (self.person_id, self.location_id):
            if partner and (partner.partner_latitude or partner.partner_longitude):
                points.append((partner.partner_longitude, partner.partner_latitude))
        return self.env["fsm.route.dayroute"]._osrm_path(points)
