# Copyright (C) 2018 Open Source Integrators
# Copyright (C) 2023 - TODAY Pytech SRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    shape = fields.GeoPoint(related="location_id.shape", string="Coordinate")

    def geo_localize(self):
        self.mapped("location_id").geo_localize()
