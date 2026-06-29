# Copyright (C) 2024 Open Source Integrators (<https://www.graymatterlogic.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    expense_ids = fields.One2many(
        "hr.expense",
        "fsm_order_id",
        string="Expenses",
    )
    expense_count = fields.Integer(compute="_compute_expense_count")

    @api.depends("expense_ids")
    def _compute_expense_count(self):
        for order in self:
            order.expense_count = len(order.expense_ids)

    def action_view_expenses(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "hr_expense.hr_expense_actions_my_all"
        )
        expenses = self.expense_ids
        if len(expenses) == 1:
            action["views"] = [
                (self.env.ref("hr_expense.hr_expense_view_form").id, "form")
            ]
            action["res_id"] = expenses.id
        else:
            action["domain"] = [("fsm_order_id", "=", self.id)]
        action["context"] = dict(
            self.env.context,
            default_fsm_order_id=self.id,
        )
        return action
