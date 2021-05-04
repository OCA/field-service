# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def prepare_fsm_values(self, fsm_order):
        res = super().prepare_fsm_values(fsm_order)
        if res.get('batch_id', False) and fsm_order:
            fsm_order.dayroute_id.batch_picking_id = \
                res.get('batch_id', False)
        return res
