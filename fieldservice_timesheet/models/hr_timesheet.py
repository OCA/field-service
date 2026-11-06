# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    fsm_order_id = fields.Many2one(
        comodel_name="fsm.order",
        string="Field Service Order",
        domain=[("project_id", "!=", False)],
    )
