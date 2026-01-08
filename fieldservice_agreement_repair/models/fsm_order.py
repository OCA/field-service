# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author: Italo Lopes <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    def _prepare_repair_order_vals(self, equipment):
        # Use the equipment agreement, fallback to the order agreement
        vals = super()._prepare_repair_order_vals(equipment)
        agreement = equipment.agreement_id or self.agreement_id
        if agreement:
            vals.update({"agreement_id": agreement.id})
        return vals
