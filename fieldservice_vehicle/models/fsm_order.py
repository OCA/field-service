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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("vehicle_id") and vals.get("person_id"):
                self._onchange_person_id()
        return super().create(vals_list)

    @api.onchange("person_id")
    def _onchange_person_id(self):
        self.vehicle_id = (
            self.person_id
            and self.person_id.vehicle_id
            and self.person_id.vehicle_id.id
            or False
        )
