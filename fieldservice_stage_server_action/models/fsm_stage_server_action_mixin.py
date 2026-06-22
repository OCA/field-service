# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class FsmStageServerActionMixin(models.AbstractModel):
    _name = "fsm.stage.server.action.mixin"
    _description = "Fsm Stage Server Action Mixin"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            action = record.stage_id.action_id
            if not action:
                continue
            context = {
                "active_model": self._name,
                "active_id": record.id,
            }
            action.with_context(**context).run()
        return records

    def write(self, vals):
        records = "stage_id" in vals and self.filtered(
            lambda ticket: ticket.stage_id.id != vals.get("stage_id")
        )
        if records:
            res = super().write(vals)
            action = self.env["fsm.stage"].browse(vals["stage_id"]).action_id
            if action:
                context = {
                    "active_model": self._name,
                    "active_ids": records.ids,
                }
                action.with_context(**context).run()
        else:
            res = super().write(vals)
        return res
