# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            action = record.stage_id.action_id
            if action:
                context = {
                    "active_model": self._name,
                    "active_ids": [record.id],
                }
                action.with_context(**context).run()
        return records

    def write(self, vals):
        res = super().write(vals)
        if "stage_id" in vals:
            for record in self:
                if record.stage_id.id != vals.get("stage_id"):
                    action = (
                        self.env["fsm.stage"].browse(vals["stage_id"]).action_id
                        if "stage_id" in vals
                        else None
                    )
                    if action:
                        context = {
                            "active_model": record._name,
                            "active_ids": record.ids,
                        }
                        action.with_context(**context).run()
                else:
                    self.activity_ids.create(
                        {
                            "res_id": self.id,
                            "res_model_id": self.env["ir.model"]
                            .search([("model", "=", "fsm.order")], limit=1)
                            .id,
                            "activity_type_id": 1,
                        }
                    )
        return res
