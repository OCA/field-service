# Copyright (C) 2026 - Gray Matter Logic
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    purchase_ids = fields.Many2many("purchase.order")
    purchase_count = fields.Integer(
        compute="_compute_purchase_count", string="# Purchases"
    )

    @api.depends("purchase_ids")
    def _compute_purchase_count(self):
        for fsm_order in self:
            fsm_order.purchase_count = len(fsm_order.purchase_ids.ids)

    def action_view_purchases(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "purchase.purchase_form_action"
        )
        action["domain"] = [("id", "in", self.purchase_ids.ids)]
        return action
