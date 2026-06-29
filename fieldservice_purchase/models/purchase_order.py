# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    fsm_order_id = fields.Many2one("fsm.order", string="FSM Order")

    def action_view_fsm_order(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "fsm.order",
            "view_mode": "form",
            "res_id": self.fsm_order_id.id,
            "target": "current",
            "name": self.env._("FSM Order: %s", self.fsm_order_id.name),
        }
