# Copyright (C) 2026 Innovyou
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    fsm_sale_line_id = fields.Many2one(
        "sale.order.line",
        string="FSM Sale Order Line",
        copy=False,
        index=True,
        help="Sale order line on which this field service timesheet has been "
        "billed.",
    )

    def _fsm_is_billed_by_sale_line(self):
        """Whether sale_timesheet already counts this timesheet in the
        delivered quantity of its sale order item."""
        self.ensure_one()
        return bool(
            self.project_id and self.so_line.qty_delivered_method == "timesheet"
        )
