# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockRequest(models.Model):
    _inherit = 'stock.request'

    fsm_order_id = fields.Many2one(
        'fsm.order', string="FSM Order", ondelete='cascade',
        index=True, copy=False)

    @api.onchange('direction', 'fsm_order_id')
    def _onchange_location_id(self):
        if self.direction == 'outbound':
            # Inventory location of the FSM location of the order
            self.location_id = \
                self.fsm_order_id.location_id.inventory_location_id.id
        else:
            # Otherwise the stock location of the warehouse
            self.location_id = \
                self.fsm_order_id.warehouse_id.lot_stock_id.id

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if 'fsm_order_id' in vals:
            fsm_order = self.env['fsm.order'].browse(vals['fsm_order_id'])
            fsm_order.write({'request_stage': 'draft'})
        return res

    def _prepare_procurement_values(self, group_id=False):
        res = self.super()._prepare_procurement_values(group_id=group_id)
        res.update({
            'fsm_order_id': self.fsm_order_id.id,
            'partner_id': self.fsm_order_id.location_id.partner_id.id,
        })
        return res
