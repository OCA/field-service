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
