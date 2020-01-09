# Copyright (C) 2019 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _link_pickings_to_fsm(self):
        for order in self:
            # TODO: We may want to split the picking to have one picking
            #  per FSM order
            fsm_order = self.env['fsm.order'].search([
                ('sale_id', '=', order.id),
                ('sale_line_id', '=', False),
            ])
            pickings = order.picking_ids
            for picking in pickings:
                picking.fsm_order_id = fsm_order.id
                for move in picking.move_lines:
                    move.fsm_order_id = move.sale_line_id.fsm_order_id.id

    @api.multi
    def _action_confirm(self):
        """ On SO confirmation, link the fsm order on the pickings
            created by the sale order """
        res = super()._action_confirm()
        self._link_pickings_to_fsm()
        return res
