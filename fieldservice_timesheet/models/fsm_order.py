# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    timesheet_ids = fields.One2many(
        comodel_name="account.analytic.line",
        inverse_name="fsm_order_id",
        string="Timesheet",
    )
