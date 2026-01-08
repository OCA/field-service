# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class FSMRecurring(models.Model):
    _inherit = "fsm.recurring"

    agreement_id = fields.Many2one("agreement", string="Agreement", copy=False)

    def _prepare_order_values(self, date=None):
        res = super()._prepare_order_values(date)
        res["agreement_id"] = self.agreement_id.id
        return res
