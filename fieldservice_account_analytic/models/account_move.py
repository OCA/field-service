# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("fsm_order_ids") and len(vals.get("fsm_order_ids")[0]) > 2:
                fsm_orders = vals.get("fsm_order_ids")[0][2]
                for order in self.env["fsm.order"].browse(fsm_orders).exists():
                    if order.location_id.analytic_account_id:
                        vals["analytic_distribution"] = {
                            order.location_id.analytic_account_id.id: 100
                        }
                    else:
                        raise ValidationError(
                            _("No analytic account " "set on the order's Location.")
                        )
        return super(AccountMoveLine, self).create(vals_list)
