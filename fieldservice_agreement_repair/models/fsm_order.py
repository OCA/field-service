# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author: Italo Lopes <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    def _create_linked_repair_order(self):
        res = super()._create_linked_repair_order()
        for order in self:
            # Use the equipment agreement, fallback to the order agreement
            agreement = order.equipment_id.agreement_id or order.agreement_id
            if agreement and order.repair_id.agreement_id != agreement:
                order.repair_id.agreement_id = agreement
        return res
