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
            self._update_vals_with_account_id(order, vals)
        return super(AccountAnalyticLine, self).create(vals)

    def _update_vals_with_account_id(self, order, vals):
        analytic_account = order.location_id.analytic_account_id
        if analytic_account:
            vals["account_id"] = analytic_account.id
        else:
            raise ValidationError(_("No analytic account set on the order's Location."))

    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
