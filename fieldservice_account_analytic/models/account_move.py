# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            order = self.env["fsm.order"].browse(vals.get("fsm_order_id"))
            if order:
                if order.location_id.analytic_account_id:
                    vals[
                        "analytic_account_id"
                    ] = order.location_id.analytic_account_id.id
                else:
                    raise ValidationError(
                        _("No analytic account " "set on the order's Location.")
                    )
        return super(AccountMoveLine, self).create(vals_list)
