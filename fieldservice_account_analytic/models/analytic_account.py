# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    fsm_order_id = fields.Many2one("fsm.order", string="FSM Order")
    product_id = fields.Many2one("product.product", string="Time Type")

    @api.model
    def create(self, vals):
        order = self.env["fsm.order"].browse(vals.get("fsm_order_id"))
        if order:
            if order.location_id.analytic_account_id:
                vals["account_id"] = order.location_id.analytic_account_id.id
            else:
                raise ValidationError(
                    _("No analytic account set " "on the order's Location.")
                )
        return super(AccountAnalyticLine, self).create(vals)

    @api.onchange("product_id")
    def onchange_product_id(self):
        self.name = self.product_id.name if self.product_id else False
