# Copyright (C) 2024 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    fsm_order_id = fields.Many2one("fsm.order", string="FSM Order")

    def action_view_order(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "fsm.order",
            "view_mode": "form",
            "res_id": self.fsm_order_id.id,
            "target": "current",
            "name": self.env._("Order: %s", self.fsm_order_id.name),
        }
