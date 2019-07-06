# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_new_picking_values(self):
        vals = super(StockMove, self)._get_new_picking_values()
        vals['carrier_id'] = self.fsm_order_id.carrier_id.id
        return vals


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    carrier_id = fields.Many2one('delivery.carrier', string="Delivery Method")
