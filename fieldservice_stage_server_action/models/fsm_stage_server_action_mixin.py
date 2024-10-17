# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class FsmStageServerActionMixin(models.AbstractModel):
    _name = "fsm.stage.server.action.mixin"
    _description = "Fsm Stage Server Action Mixin"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._run_stage_server_action()
        return records

    def write(self, vals):
        res = super().write(vals)
        if "stage_id" in vals:
            self._run_stage_server_action()
        return res

    def _run_stage_server_action(self):
        for record in self:
            action_id = record.stage_id.action_id
            if not action_id:
                continue
            ctx = {
                "active_model": self._name,
                "active_id": [record.id],
            }
            action_id.with_context(**ctx).run()
