# Copyright (C) 2018 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _action_done(self):
        res = super(StockMoveLine, self)._action_done()
        for rec in self:
            if rec.move_id:
                for request in rec.move_id.allocation_ids:
                    if (request.stock_request_id.state == 'done'
                            and request.stock_request_id.fsm_order_id):
                        request.stock_request_id.\
                            fsm_order_id.request_stage = 'done'
        return res
