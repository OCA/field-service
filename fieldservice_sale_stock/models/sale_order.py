# Copyright (C) 2019 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _link_pickings_to_fsm(self):
        for order in self:
            fsm_order = self.env['fsm.order'].search([
                ('sale_id', '=', order.id)
            ])
            pickings = order.picking_ids
            pickings.write({'fsm_order_id': fsm_order.id})

    @api.multi
    def action_confirm(self):
        """ On SO confirmation, link the fsm order on the pickings
            created by the sale order """
        result = super().action_confirm()
        self._link_pickings_to_fsm()
        return result
