# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    fsm_order_id = fields.Many2one("fsm.order", string="FSM Order")
    product_id = fields.Many2one("product.product", string="Time Type")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("fsm_order_id"):
                order = self.env["fsm.order"].browse(vals["fsm_order_id"])
                account = order.location_id.analytic_account_id
                if account:
                    # Each analytic plan has its own column on the line:
                    # store the location account on the column of its plan.
                    vals[account.plan_id._column_name()] = account.id
        lines = super().create(vals_list)
        lines._check_fsm_order_analytic_account()
        return lines

    def _check_fsm_order_analytic_account(self):
        for line in self.filtered("fsm_order_id"):
            if not any(line[fname] for fname in line._get_plan_fnames()):
                raise ValidationError(
                    self.env._("No analytic account set on the order's Location.")
                )
