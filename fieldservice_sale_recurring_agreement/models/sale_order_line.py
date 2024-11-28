# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author: Italo Lopes <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _field_create_fsm_recurring_prepare_values(self):
        res = super()._field_create_fsm_recurring_prepare_values()
        if self.order_id and self.order_id.agreement_id:
            res["agreement_id"] = self.order_id.agreement_id.id
        return res
