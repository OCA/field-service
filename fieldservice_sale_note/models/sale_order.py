# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    internal_note = fields.Text()

    def _field_service_generate(self):
        res = super()._field_service_generate()
        for order in res:
            if self.internal_note:
                order.resolution = self.internal_note
        return res

    def write(self, values):
        res = super().write(values)
        if "internal_note" in values:
            for order in self.fsm_order_ids:
                order.resolution = values["internal_note"]
        return res
