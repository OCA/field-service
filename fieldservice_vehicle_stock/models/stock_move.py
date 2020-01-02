# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        if self.picking_id.fsm_order_ids:
            self = self.with_context(
                vehicle_id=self.picking_id.fsm_order_ids[0].vehicle_id.id)
        return super()._prepare_move_line_vals(
            quantity, reserved_quant)
