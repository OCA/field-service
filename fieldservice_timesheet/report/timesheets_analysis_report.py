# Copyright (C) 20224 Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import SQL


class TimesheetsAnalysisReport(models.Model):
    _inherit = "timesheets.analysis.report"

    fsm_order_id = fields.Many2one(
        "fsm.order",
        string="Field Service Order",
        readonly=True,
    )

    @api.model
    def _select(self):
        return SQL("%s, A.fsm_order_id AS fsm_order_id", super()._select())
