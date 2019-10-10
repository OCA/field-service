# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta
from odoo import api, fields, models


class StockRequest(models.Model):
    _inherit = 'stock.request'

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

    def prepare_order_values(self, vals):
        res = {
            'expected_date': vals['expected_date'],
            'picking_policy': vals['picking_policy'],
            'warehouse_id': vals['warehouse_id'],
            'direction': vals['direction'],
            'location_id': vals['location_id'],
        }
        if 'fsm_order_id' in vals and vals['fsm_order_id']:
            res.update({'fsm_order_id': vals['fsm_order_id']})
        return res

    @api.model
    def create(self, vals):
        if 'fsm_order_id' in vals and vals['fsm_order_id']:
            fsm_order = self.env['fsm.order'].browse(vals['fsm_order_id'])
            fsm_order.request_stage = 'draft'

            val_date = vals['expected_date']
            if not isinstance(vals['expected_date'], str):
                val_date = datetime.strftime(vals['expected_date'],
                                             '%Y-%m-%d %H:%M:%S')

            val_date = datetime.strptime(val_date, '%Y-%m-%d %H:%M:%S')
            date_window_after = val_date - timedelta(hours=1)

            order = self.env['stock.request.order'].search([
                ('fsm_order_id', '=', vals['fsm_order_id']),
                ('direction', '=', vals['direction']),
                ('expected_date', '>', date_window_after),
                ('state', '=', 'draft')
            ])
            if order:
                vals['expected_date'] = order.expected_date
                vals['order_id'] = order.id
            else:
                values = self.prepare_order_values(vals)
                vals['order_id'] = self.env['stock.request.order'].\
                    create(values).id
        return super().create(vals)

    def _prepare_procurement_values(self, group_id=False):
        res = super()._prepare_procurement_values(group_id=group_id)
        if self.fsm_order_id:
            res.update({
                'fsm_order_id': self.fsm_order_id.id,
                'partner_id':
                    self.fsm_order_id.location_id.shipping_address_id.id or
                    self.fsm_order_id.location_id.partner_id.id
            })
        return res

    def _prepare_procurement_group_values(self):
        if self.fsm_order_id:
            order = self.env['fsm.order'].browse(self.fsm_order_id.id)
            return {'name': order.name,
                    'fsm_order_id': order.id,
                    'move_type': 'direct'}
        else:
            return {}

    @api.multi
    def _action_confirm(self):
        for req in self:
            if (not req.procurement_group_id) and req.fsm_order_id:
                fsm_order = self.env['fsm.order'].browse(req.fsm_order_id.id)
                group = self.env['procurement.group'].search([
                    ('fsm_order_id', '=', fsm_order.id)])
                if not group:
                    values = req._prepare_procurement_group_values()
                    group = req.env['procurement.group'].create(values)
                if req.order_id:
                    req.order_id.procurement_group_id = group.id
                req.procurement_group_id = group.id
                res = super(StockRequest, req)._action_confirm()
                fsm_order.request_stage = 'open'
            else:
                res = super(StockRequest, req)._action_confirm()
        return res
