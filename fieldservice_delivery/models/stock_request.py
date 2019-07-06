# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockRequest(models.Model):
    _inherit = 'stock.request'

    carrier_id = fields.Many2one('delivery.carrier', string="Delivery Method")

    def _prepare_procurement_values(self, group_id=False):
        res = super()._prepare_procurement_values(group_id=group_id)
        res.update({
            'carrier_id': self.fsm_order_id.carrier_id.id or False,
        })
        return res
