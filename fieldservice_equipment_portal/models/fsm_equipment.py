# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class FsmEquipment(models.Model):
    _name = "fsm.equipment"
    _inherit = ["fsm.equipment", "portal.mixin"]

    def _compute_access_url(self):
        res = super()._compute_access_url()
        for record in self:
            record.access_url = f"/my/equipments/{record.id}"
        return res
