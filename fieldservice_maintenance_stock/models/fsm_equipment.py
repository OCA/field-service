# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class FSMEquipment(models.Model):
    _inherit = "fsm.equipment"

    def _prepare_maintenance_vals(self, vals):
        res = super()._prepare_maintenance_vals(vals)
        res.update({"product_id": vals.get("product_id"), "lot_id": vals.get("lot_id")})
        return res
