# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    fsm_order_id = fields.Many2one("fsm.order", string="FSM Order")
    product_id = fields.Many2one("product.product", string="Time Type")

    @api.constrains("fsm_order_id")
    def _check_fsm_order_id(self):
        for line in self:
            if (
                line.fsm_order_id
                and not line.fsm_order_id.location_id.analytic_account_id
            ):
                raise ValidationError(
                    _(
                        "No analytic account set on the order's Location "
                        "%(location_name)s. Please set an analytic account on the "
                        "Location before creating an analytic line for this order.",
                        location_name=line.fsm_order_id.location_id.name,
                    )
                )

    @api.onchange("product_id")
    def onchange_product_id(self):
        self.name = self.product_id.name if self.product_id else False
