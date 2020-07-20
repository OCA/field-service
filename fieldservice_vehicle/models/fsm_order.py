# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    @api.model
    def _get_default_vehicle(self):
        return self.person_id.vehicle_id.id or False

    vehicle_id = fields.Many2one(
        "fsm.vehicle", string="Vehicle", default=_get_default_vehicle
    )

    @api.model
    def create(self, vals):
        if not vals.get("vehicle_id") and vals.get("person_id"):
            person = self.env["fsm.person"].browse(vals.get("person_id"))
            vals.update({"vehicle_id": person.vehicle_id.id})
        return super().create(vals)
