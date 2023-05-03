# Copyright (C) 2019 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def prepare_fsm_values_for_stock_move(self, fsm_order):
        return {
            "fsm_order_id": fsm_order.id,
        }

    def prepare_fsm_values_for_stock_picking(self, fsm_order):
        return {
            "fsm_order_id": fsm_order.id,
        }

    def _link_pickings_to_fsm(self):
        for rec in self:
            # TODO: We may want to split the picking to have one picking
            # per FSM order
            fsm_order = self.env["fsm.order"].search(
                [
                    ("sale_id", "=", rec.id),
                    ("sale_line_id", "=", False),
                ]
            )
            if rec.procurement_group_id:
                rec.procurement_group_id.fsm_order_id = fsm_order.id or False
            for picking in rec.picking_ids:
                picking.write(rec.prepare_fsm_values_for_stock_picking(fsm_order))
                for move in picking.move_lines:
                    move.write(rec.prepare_fsm_values_for_stock_move(fsm_order))

    def _action_confirm(self):
        """On SO confirmation, link the fsm order on the pickings
        created by the sale order"""
        res = super()._action_confirm()
        self._link_pickings_to_fsm()
        return res
