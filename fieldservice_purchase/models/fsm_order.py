# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    purchase_ids = fields.One2many("purchase.order", "fsm_order_id")
    purchase_count = fields.Integer(
        compute="_compute_purchase_count", string="# Purchases"
    )

    @api.depends("purchase_ids")
    def _compute_purchase_count(self):
        for order in self:
            order.purchase_count = len(order.purchase_ids)

    def action_view_purchases(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "purchase.purchase_form_action"
        )
        action["domain"] = [("fsm_order_id", "=", self.id)]
        action["context"] = {
            **self.env.context,
            "default_fsm_order_id": self.id,
        }
        if len(self.purchase_ids) == 1:
            action["views"] = [
                (self.env.ref("purchase.purchase_order_form").id, "form")
            ]
            action["res_id"] = self.purchase_ids.id
        return action
