# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends("fsm_order_ids")
    def _compute_analytic_distribution(self):
        res = super()._compute_analytic_distribution()
        for line in self:
            analytic_account = line._get_fsm_analytic_account()
            if analytic_account:
                line.analytic_distribution = {str(analytic_account.id): 100}
        return res

    def _get_fsm_analytic_account(self):
        """Return the analytic account to apply on the move line,
        based on the location of the linked Field Service orders.

        Kept as a separate method to ease overrides in other modules.
        """
        self.ensure_one()
        analytic_account = self.env["account.analytic.account"]
        for order in self.fsm_order_ids:
            if order.location_id.analytic_account_id:
                analytic_account = order.location_id.analytic_account_id
        return analytic_account

    @api.constrains("fsm_order_ids")
    def _check_fsm_order_analytic_account(self):
        for line in self:
            for order in line.fsm_order_ids:
                if not order.location_id.analytic_account_id:
                    raise ValidationError(
                        self.env._("No analytic account set on the order's Location.")
                    )
