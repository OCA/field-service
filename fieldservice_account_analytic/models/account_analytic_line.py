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
                if order.location_id.analytic_account_id:
                    vals["account_id"] = order.location_id.analytic_account_id.id
                else:
                    raise ValidationError(
                        self.env._("No analytic account set on the order's Location.")
                    )
        return super().create(vals_list)
