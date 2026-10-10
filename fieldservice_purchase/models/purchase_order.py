# Copyright (C) 2026 - Gray Matter Logic
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    fsm_order_ids = fields.Many2many("fsm.order")
    fsm_order_count = fields.Integer(
        compute="_compute_fsm_order_count", string="# FSM Orders"
    )

    @api.depends("fsm_order_ids")
    def _compute_fsm_order_count(self):
        for purchase in self:
            purchase.fsm_order_count = len(purchase.fsm_order_ids.ids)

    def action_view_fsm_orders(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "fieldservice.action_fsm_dash_order"
        )
        action["domain"] = [("id", "in", self.fsm_order_ids.ids)]
        return action
