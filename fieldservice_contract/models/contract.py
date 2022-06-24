# Copyright 2019 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    fsm_location_id = fields.Many2one(
        string="FSM Location",
        comodel_name="fsm.location",
        inverse_name="contract_ids",
        copy=True,
        help="Default Location",
    )

    def action_view_fsm_recurring(self):
        fsm_recurrings = self.contract_line_ids.mapped("fsm_recurring_id")
        action = self.env.ref("fieldservice_recurring.action_fsm_recurring").read()[0]
        if len(fsm_recurrings) > 1:
            action["domain"] = [("id", "in", fsm_recurrings.ids)]
        elif len(fsm_recurrings) == 1:
            action["views"] = [
                (
                    self.env.ref("fieldservice_recurring.fsm_recurring_form_view").id,
                    "form",
                )
            ]
            action["res_id"] = fsm_recurrings.id
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action

    def action_view_fsm_order(self):
        # fetch all orders:
        #    - created directly
        #    - created by recurring
        line_ids = self.contract_line_ids.ids
        action = self.env.ref("fieldservice.action_fsm_dash_order").read()[0]
        action["domain"] = [("contract_line_id", "in", line_ids)]
        return action
