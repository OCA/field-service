# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_fsm_values(self, **kwargs):
        # OVERRIDE to propagate the agreement_id to the FSM Order
        res = super()._prepare_fsm_values(**kwargs)
        res.update({"agreement_id": self.agreement_id.id})
        return res
