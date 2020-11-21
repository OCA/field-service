# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import exceptions, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _action_done(self):
        res = super()._action_done()
        for rec in self:
            # cases were found where self contained deleted records
            # example is creating a backorder for Products with lot number
            try:
                move_id = rec.move_id
            except exceptions.MissingError:
                move_id = None
            if move_id:
                for request in rec.move_id.allocation_ids:
                    if (
                        request.stock_request_id.state == "done"
                        and request.stock_request_id.fsm_order_id
                    ):
                        request.stock_request_id.fsm_order_id.request_stage = "done"
        return res
