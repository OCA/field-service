# Copyright (C) 2019 Brian McMaster, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    fsm_recurring_id = fields.Many2one(
        "fsm.recurring", "Recurring Order", readonly=True
    )

    def _compute_request_late(self):
        for rec in self:
            if not rec.fsm_recurring_id:
                return super(FSMOrder, self)._compute_request_late()
            else:
                days_late = rec.fsm_recurring_id.fsm_frequency_set_id.buffer_late
                rec.request_late = rec.scheduled_date_start + timedelta(days=days_late)

    def action_view_fsm_recurring(self):
        action = self.env.ref("fieldservice_recurring.action_fsm_recurring").read()[0]
        action["views"] = [
            (self.env.ref("fieldservice_recurring.fsm_recurring_form_view").id, "form")
        ]
        action["res_id"] = self.fsm_recurring_id.id
        return action
