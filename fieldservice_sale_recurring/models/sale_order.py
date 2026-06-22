# Copyright (C) 2019 Brian McMaster
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    fsm_recurring_ids = fields.Many2many(
        "fsm.recurring",
        compute="_compute_fsm_recurring_ids",
        string="Field Service Recurring orders associated to this sale",
    )
    fsm_recurring_count = fields.Float(
        string="FSM Recurring Orders", compute="_compute_fsm_recurring_ids"
    )

    @api.depends("order_line.product_id")
    def _compute_fsm_recurring_ids(self):
        for order in self:
            order.fsm_recurring_ids = self.env["fsm.recurring"].search(
                [("sale_line_id", "in", order.order_line.ids)]
            )
            order.fsm_recurring_count = len(order.fsm_recurring_ids)

    def action_view_fsm_recurring(self):
        fsm_recurrings = self.mapped("fsm_recurring_ids")
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

    def _action_confirm(self):
        """On SO confirmation, some lines generate field service recurrings."""
        result = super()._action_confirm()
        self.order_line.filtered(
            lambda line: line.product_id.field_service_tracking == "recurring"
            and not line.fsm_recurring_id
        )._field_create_fsm_recurring()
        return result
