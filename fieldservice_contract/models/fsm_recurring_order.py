# Copyright 2019 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMRecurringOrder(models.Model):
    _inherit = "fsm.recurring"

    contract_line_id = fields.Many2one(
        comodel_name="contract.line",
        inverse_name="fsm_recurring_id",
        readonly=True,
    )

    def _prepare_order_values(self, date=None):
        res = super()._prepare_order_values(date)
        res["contract_line_id"] = self.contract_line_id.id
        return res

