# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _field_create_fsm_recurring_prepare_values(self):
        res = super()._field_create_fsm_recurring_prepare_values()
        if self.order_id and self.order_id.agreement_id:
            res["agreement_id"] = self.order_id.agreement_id.id
        return res
