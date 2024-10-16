# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockRequestOrder(models.Model):
    _inherit = 'stock.request.order'

    fsm_order_id = fields.Many2one(
        'fsm.order', string="FSM Order", ondelete='cascade',
        index=True, copy=False)

    @api.onchange('direction', 'fsm_order_id')
    def _onchange_location_id(self):
        super()._onchange_location_id()
        if self.fsm_order_id:
            if self.direction == 'outbound':
                # Inventory location of the FSM location of the order
                self.location_id = \
                    self.fsm_order_id.location_id.inventory_location_id.id
            else:
                # Otherwise the stock location of the warehouse
                self.location_id = \
                    self.fsm_order_id.warehouse_id.lot_stock_id.id
        self.change_childs()

    def change_childs(self):
        super().change_childs()
        if not self._context.get('no_change_childs', False):
            for line in self.stock_request_ids:
                line.fsm_order_id = self.fsm_order_id.id

    def _prepare_procurement_group_values(self):
        if self.fsm_order_id:
            order = self.env['fsm.order'].browse(self.fsm_order_id.id)
            return {'name': order.name,
                    'fsm_order_id': order.id,
                    'move_type': 'direct'}
        else:
            return {}

    @api.multi
    def action_confirm(self):
        if self.fsm_order_id:
            fsm_order = self.env['fsm.order'].browse(self.fsm_order_id.id)
            group = self.env['procurement.group'].search([
                ('fsm_order_id', '=', fsm_order.id)])
            if not group:
                values = self._prepare_procurement_group_values()
                group = self.env['procurement.group'].create(values)
            self.procurement_group_id = group[0].id
            self.change_childs()
        return super().action_confirm()
