# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        orders._run_stage_server_action()
        return orders

    def write(self, vals):
        res = super().write(vals)
        if "stage_id" in vals:
            self._run_stage_server_action()
        return res

    def _run_stage_server_action(self):
        for order in self:
            action_id = order.stage_id.action_id
            if not action_id:
                continue
            ctx = {
                "active_model": self._name,
                "active_id": order.id,
            }
            action_id.with_context(**ctx).run()
