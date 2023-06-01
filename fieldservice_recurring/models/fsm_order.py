# Copyright (C) 2019 Brian McMaster, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    fsm_recurring_id = fields.Many2one(
        "fsm.recurring", "Recurring Order", readonly=True
    )

    @api.model
    def create(self, vals):
        if vals.get("fsm_recurring_id", False) and vals.get(
            "scheduled_date_start", False
        ):
            days_late = (
                self.env["fsm.recurring"]
                .browse(vals["fsm_recurring_id"])
                .fsm_frequency_set_id.buffer_late
            )
            vals["request_late"] = vals["scheduled_date_start"] + timedelta(
                days=days_late
            )
        return super().create(vals)

    def action_view_fsm_recurring(self):
        action = self.env.ref("fieldservice_recurring.action_fsm_recurring").read()[0]
        action["views"] = [
            (self.env.ref("fieldservice_recurring.fsm_recurring_form_view").id, "form")
        ]
        action["res_id"] = self.fsm_recurring_id.id
        return action
