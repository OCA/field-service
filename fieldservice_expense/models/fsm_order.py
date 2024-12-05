# Copyright (C) 2024 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    expense_ids = fields.One2many(
        "hr.expense",
        "fsm_order_id",
    )

    expense_count = fields.Integer(compute="_compute_expenses")

    @api.depends("expense_ids")
    def _compute_expenses(self):
        for record in self:
            record.expense_count = len(record.expense_ids)

    def action_view_expenses(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.expense",
            "view_mode": "list,form",
            "domain": [("fsm_order_id", "=", self.id)],
            "context": {"default_fsm_order_id": self.id},
            "name": _("Expenses for FSM Order %s") % self.name,
        }
