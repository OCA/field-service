# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import api, fields, models, _

from odoo.tools import (DEFAULT_SERVER_DATETIME_FORMAT,
                        float_is_zero, float_compare)
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

from odoo.addons.base_geoengine import geo_model

STOCK_STAGES = [('draft', 'Draft'),
                ('requested', 'Requested'),
                ('confirmed', 'Confirmed'),
                ('partial', 'Partially Shipped'),
                ('done', 'Done'),
                ('cancelled', 'Cancelled')]


class FSMOrder(geo_model.GeoModel):
    _inherit = 'fsm.order'

    @api.model
    def _default_warehouse_id(self):
        company = self.env.user.company_id.id
        warehouse_ids = self.env['stock.warehouse'].search(
            [('company_id', '=', company)], limit=1)
        return warehouse_ids

    line_ids = fields.One2many('fsm.order.line', 'order_id',
                               string="Order Lines")
    picking_ids = fields.One2many('stock.picking', 'fsm_order_id',
                                  string='Transfers')
    delivery_count = fields.Integer(string='Delivery Orders',
                                    compute='_compute_picking_ids')
    procurement_group_id = fields.Many2one(
        'procurement.group', 'Procurement Group', copy=False)
    inventory_location_id = fields.Many2one(
        related='location_id.inventory_location_id', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse',
                                   required=True, readonly=True,
                                   default=_default_warehouse_id,
                                   help="Warehouse used to ship the materials")
    # FSM Order return
    return_ids = fields.One2many('fsm.order.return', 'order_id',
                                 string="Return Lines")
    return_count = fields.Integer(string='Return Orders',
                                  compute='_compute_picking_ids')
    inventory_stage = fields.Selection(STOCK_STAGES, string='State',
                                       default='draft', required=True,
                                       readonly=True, store=True)

    @api.depends('picking_ids')
    def _compute_picking_ids(self):
        for order in self:
            order.delivery_count = len(
                [picking for picking in order.picking_ids if
                 picking.picking_type_id.code == 'outgoing'])
            order.return_count = len(
                [picking for picking in order.picking_ids if
                 picking.picking_type_id.code == 'incoming'])

    def action_inventory_request(self):
        if self.location_id and (self.line_ids or self.return_ids) and\
                self.warehouse_id:
            for line in self.line_ids:
                if line.state == 'draft':
                    line.state = 'requested'
                    line.qty_ordered = line.qty_requested
            for line in self.return_ids:
                if line.state == 'draft':
                    line.state = 'requested'
                    line.qty_ordered = line.qty_requested
            self.inventory_stage = 'requested'
        else:
            raise UserError(
                _('Please select the location, a warehouse and a product.'))

    def action_inventory_confirm(self):
        if self.location_id and (self.line_ids or self.return_ids) and\
                self.warehouse_id:
            if self.line_ids:
                line_ids = self.mapped('line_ids').filtered(
                    lambda l: l.state == 'requested')
                line_ids._confirm_picking()
            if self.return_ids:
                return_ids = self.mapped('return_ids').filtered(
                    lambda l: l.state == 'requested')
                return_ids._confirm_picking()
            self.inventory_stage = 'confirmed'
        else:
            raise UserError(
                _('Please select the location, a warehouse and a product.'))

    def action_inventory_cancel(self):
        if self.line_ids:
            line_ids = self.mapped('line_ids').filtered(
                lambda l: l.state == 'requested')
            for line in line_ids:
                line.state = 'cancelled'
        if self.return_ids:
            return_ids = self.mapped('return_ids').filtered(
                lambda l: l.state == 'requested')
            for line in return_ids:
                line.state = 'cancelled'
        self.inventory_stage = 'cancelled'

    def action_inventory_reset(self):
        if self.line_ids:
            line_ids = self.mapped('line_ids').filtered(
                lambda l: l.state == 'cancelled')
            for line in line_ids:
                line.state = 'draft'
        if self.return_ids:
            return_ids = self.mapped('return_ids').filtered(
                lambda l: l.state == 'cancelled')
            for line in return_ids:
                line.state = 'draft'
        self.inventory_stage = 'draft'

    @api.multi
    def action_view_delivery(self):
        '''
        This function returns an action that display existing delivery orders
        of given fsm order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        pickings = self.mapped('picking_ids')
        delivery_ids = [picking.id for picking in pickings if
                        picking.picking_type_id.code == 'outgoing']
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', delivery_ids)]
        elif pickings:
            action['views'] = [(self.env.ref('stock.view_picking_form').id,
                                'form')]
            action['res_id'] = pickings.id
        return action

    @api.multi
    def action_view_returns(self):
        '''
        This function returns an action that display existing return orders
        of given fsm order ids. It can either be a in a list or in a form
        view, if there is only one return order to show.
        '''
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        pickings = self.mapped('picking_ids')
        receipt_ids = [picking.id for picking in pickings if
                       picking.picking_type_id.code == 'incoming']
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', receipt_ids)]
        elif pickings:
            action['views'] = [(self.env.ref('stock.view_picking_form').id,
                                'form')]
            action['res_id'] = pickings.id
        return action


class FSMOrderLine(models.Model):
    _name = 'fsm.order.line'
    _description = "FSM Order Lines"
    _order = 'order_id, sequence, id'

    order_id = fields.Many2one(
        'fsm.order', string="FSM Order", required=True,
        ondelete='cascade', index=True, copy=False,
        readonly=True, states={'draft': [('readonly', False)]})
    name = fields.Char(string='Description', required=True,
                       readonly=True, states={'draft': [('readonly', False)]})
    sequence = fields.Integer(string='Sequence', default=10, readonly=True,
                              states={'draft': [('readonly', False)]})
    product_id = fields.Many2one(
        'product.product', string="Product",
        domain=[('type', '=', 'product')], ondelete='restrict',
        readonly=True, states={'draft': [('readonly', False)]})
    product_uom_id = fields.Many2one(
        'product.uom', string='Unit of Measure', required=True,
        readonly=True, states={'draft': [('readonly', False)]})
    qty_requested = fields.Float(
        string='Quantity Requested', readonly=True,
        states={'draft': [('readonly', False)]},
        digits=dp.get_precision('Product Unit of Measure'))
    qty_ordered = fields.Float(
        string='Quantity Ordered', readonly=True,
        states={'requested': [('readonly', False)]},
        digits=dp.get_precision('Product Unit of Measure'))
    qty_delivered = fields.Float(
        string='Quantity Delivered', readonly=True, copy=False,
        digits=dp.get_precision('Product Unit of Measure'))
    state = fields.Selection(STOCK_STAGES, string='State', required=True,
                             compute='_compute_state', default='draft',
                             copy=False, index=True, readonly=True, store=True)
    move_ids = fields.One2many(
        'stock.move', 'fsm_order_line_id', string='Stock Moves',
        readonly=True, states={'draft': [('readonly', False)]})
    route_id = fields.Many2one('stock.location.route', string='Route',
                               domain=[('fsm_selectable', '=', True)],
                               ondelete='restrict')

    @api.depends('move_ids', 'qty_ordered', 'qty_delivered')
    def _compute_state(self):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for line in self:
            if line.move_ids and not float_is_zero(line.qty_delivered,
                                                   precision_digits=precision):
                if float_compare(line.qty_delivered, line.qty_ordered,
                                 precision_digits=precision) == -1:
                    line.state = 'partial'
                elif float_compare(line.qty_delivered, line.qty_ordered,
                                   precision_digits=precision) >= 0:
                    line.state = 'done'
            elif line.move_ids:
                line.state = 'confirmed'
            else:
                if line.qty_ordered != 0:
                    line.state = 'requested'
                else:
                    line.state = 'draft'

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=',
                                   self.product_id.uom_id.category_id.id)]}

        if (not self.product_uom_id
                or (self.product_id.uom_id.id != self.product_uom_id.id)):
            vals['product_uom_id'] = self.product_id.uom_id
            vals['qty_requested'] = 1.0

        product = self.product_id.with_context(
            quantity=vals.get('qty_requested') or self.qty_requested,
            uom=self.product_uom_id.id,
        )

        result = {'domain': domain}

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        self.update(vals)
        return result

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        self.ensure_one()
        values = {}
        date_planned = (self.order_id.scheduled_date_start
                        or self.order_id.request_early
                        or self.order_id.request_late
                        or (datetime.now() + timedelta(days=1)).strftime(
                            DEFAULT_SERVER_DATETIME_FORMAT))
        values.update({
            'group_id': group_id,
            'fsm_order_line_id': self.id,
            'date_planned': date_planned,
            'route_ids':
                self.route_id or self.order_id.warehouse_id.delivery_route_id,
            'partner_dest_id': self.order_id.customer_id
        })
        return values

    def _get_procurement_qty(self):
        self.ensure_one()
        qty = 0.0
        for move in self.move_ids.filtered(lambda r: r.state != 'cancel'):
            if move.picking_code == 'outgoing':
                qty += move.product_uom._compute_quantity(
                    move.product_uom_qty, self.product_uom_id,
                    rounding_method='HALF-UP')
            elif move.picking_code == 'incoming':
                qty -= move.product_uom._compute_quantity(
                    move.product_uom_qty, self.product_uom_id,
                    rounding_method='HALF-UP')
        return qty

    @api.multi
    def _confirm_picking(self):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        errors = []
        for line in self:
            qty_procured = line._get_procurement_qty()
            if float_compare(qty_procured, line.qty_ordered,
                             precision_digits=precision) >= 0:
                continue
            group_id = line.order_id.procurement_group_id
            if not group_id:
                group_id = self.env['procurement.group'].create({
                    'name': line.order_id.name,
                    'move_type': 'direct',
                    'fsm_order_id': line.order_id.id,
                    'partner_id': line.order_id.customer_id.id,
                })
                line.order_id.procurement_group_id = group_id
            values = line._prepare_procurement_values(group_id=group_id)
            qty_needed = line.qty_ordered - qty_procured
            procurement_uom = line.product_uom_id
            quant_uom = line.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if (procurement_uom.id != quant_uom.id
                    and get_param('stock.propagate_uom') != '1'):
                qty_needed = line.product_uom_id._compute_quantity(
                    qty_needed, quant_uom, rounding_method='HALF-UP')
                procurement_uom = quant_uom
            try:
                self.env['procurement.group'].run(
                    line.product_id, qty_needed, procurement_uom,
                    line.order_id.inventory_location_id,
                    line.name, line.order_id.name, values)
            except UserError as error:
                errors.append(error.name)
        if errors:
            raise UserError('\n'.join(errors))
        return True

    @api.multi
    def _get_delivered_qty(self):
        self.ensure_one()
        qty = 0.0
        for move in self.move_ids.filtered(
                lambda r: r.state == 'done' and not r.scrapped):
            if move.location_dest_id.usage == "customer":
                if (not move.origin_returned_move_id
                        or (move.origin_returned_move_id and move.to_refund)):
                    qty += move.product_uom._compute_quantity(
                        move.product_uom_qty, self.product_uom_id)
            elif (move.location_dest_id.usage != "customer"
                  and move.to_refund):
                qty -= move.product_uom._compute_quantity(
                    move.product_uom_qty, self.product_uom_id)
        return qty

    def create(self, vals):
        res = super(FSMOrderLine, self).create(vals)
        if 'order_id' in vals:
            res.order_id.inventory_stage = 'draft'
        return res


class FSMOrderReturn(models.Model):
    _name = 'fsm.order.return'
    _description = "FSM Order Return"
    _order = 'order_id, sequence, id'

    order_id = fields.Many2one(
        'fsm.order', string="FSM Order", required=True,
        ondelete='cascade', index=True, copy=False,
        readonly=True, states={'draft': [('readonly', False)]})
    name = fields.Char(string='Description', required=True,
                       readonly=True, states={'draft': [('readonly', False)]})
    sequence = fields.Integer(string='Sequence', default=10, readonly=True,
                              states={'draft': [('readonly', False)]})
    product_id = fields.Many2one(
        'product.product', string="Product",
        domain=[('type', '=', 'product')], ondelete='restrict',
        readonly=True, states={'draft': [('readonly', False)]})
    product_uom_id = fields.Many2one(
        'product.uom', string='Unit of Measure', required=True,
        readonly=True, states={'draft': [('readonly', False)]})
    qty_requested = fields.Float(
        string='Quantity Requested', readonly=True,
        states={'draft': [('readonly', False)]},
        digits=dp.get_precision('Product Unit of Measure'))
    qty_returned = fields.Float(
        string='Quantity Returned', readonly=True,
        states={'requested': [('readonly', False)]},
        digits=dp.get_precision('Product Unit of Measure'))
    qty_received = fields.Float(
        string='Quantity Received', readonly=True, copy=False,
        digits=dp.get_precision('Product Unit of Measure'))
    state = fields.Selection(STOCK_STAGES, string='State', required=True,
                             compute='_compute_state', default='draft',
                             copy=False, index=True, readonly=True, store=True)
    move_ids = fields.One2many(
        'stock.move', 'fsm_order_return_line_id', string='Stock Moves',
        readonly=True, states={'draft': [('readonly', False)]})
    route_id = fields.Many2one('stock.location.route', string='Route',
                               domain=[('fsm_return_selectable', '=', True)],
                               ondelete='restrict')

    @api.depends('move_ids', 'qty_returned', 'qty_received')
    def _compute_state(self):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for line in self:
            if line.move_ids and not float_is_zero(line.qty_received,
                                                   precision_digits=precision):
                if float_compare(line.qty_received, line.qty_returned,
                                 precision_digits=precision) == -1:
                    line.state = 'partial'
                elif float_compare(line.qty_received, line.qty_returned,
                                   precision_digits=precision) >= 0:
                    line.state = 'done'
            elif line.move_ids:
                line.state = 'confirmed'
            else:
                line.state = 'draft'

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=',
                                   self.product_id.uom_id.category_id.id)]}

        if (not self.product_uom_id
                or (self.product_id.uom_id.id != self.product_uom_id.id)):
            vals['product_uom_id'] = self.product_id.uom_id
            vals['qty_requested'] = 1.0

        product = self.product_id.with_context(
            quantity=vals.get('qty_requested') or self.qty_requested,
            uom=self.product_uom_id.id,
        )
        result = {'domain': domain}
        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name
        self.update(vals)
        return result

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        self.ensure_one()
        values = {}
        date_planned = (self.order_id.scheduled_date_start
                        or self.order_id.request_early
                        or self.order_id.request_late
                        or (datetime.now() + timedelta(days=1)).strftime(
                            DEFAULT_SERVER_DATETIME_FORMAT))
        values.update({
            'group_id': group_id,
            'fsm_order_return_line_id': self.id,
            'date_planned': date_planned,
            'route_ids':
                self.route_id or self.order_id.warehouse_id.reception_route_id,
            'partner_dest_id': self.order_id.warehouse_id
        })
        return values

    def _get_procurement_qty(self):
        self.ensure_one()
        qty = 0.0
        for move in self.move_ids.filtered(lambda r: r.state != 'cancel'):
            if move.picking_code == 'incoming':
                qty += move.product_uom._compute_quantity(
                    move.product_uom_qty, self.product_uom_id,
                    rounding_method='HALF-UP')
            elif move.picking_code == 'outgoing':
                qty -= move.product_uom._compute_quantity(
                    move.product_uom_qty, self.product_uom_id,
                    rounding_method='HALF-UP')
        return qty

    @api.multi
    def _confirm_picking(self):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        errors = []
        for line in self:
            qty_procured = line._get_procurement_qty()
            if float_compare(qty_procured, line.qty_returned,
                             precision_digits=precision) >= 0:
                continue
            group_id = line.order_id.procurement_group_id
            if not group_id:
                group_id = self.env['procurement.group'].create({
                    'name': line.order_id.name,
                    'move_type': 'direct',
                    'fsm_order_id': line.order_id.id,
                    'partner_id': line.order_id.customer_id.id,
                })
                line.order_id.procurement_group_id = group_id
            values = line._prepare_procurement_values(group_id=group_id)
            qty_needed = line.qty_returned - qty_procured
            procurement_uom = line.product_uom_id
            quant_uom = line.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if (procurement_uom.id != quant_uom.id
                    and get_param('stock.propagate_uom') != '1'):
                qty_needed = line.product_uom_id._compute_quantity(
                    qty_needed, quant_uom, rounding_method='HALF-UP')
                procurement_uom = quant_uom
            try:
                self.env['procurement.group'].run(
                    line.product_id, qty_needed, procurement_uom,
                    line.order_id.warehouse_id.lot_stock_id,
                    line.name, line.order_id.name, values)
            except UserError as error:
                errors.append(error.name)
        if errors:
            raise UserError('\n'.join(errors))
        return True

    @api.multi
    def _get_received_qty(self):
        self.ensure_one()
        qty = 0.0
        for move in self.move_ids.filtered(
                lambda r: r.state == 'done' and not r.scrapped):
            if move.location_dest_id.usage != "customer":
                if (not move.origin_returned_move_id
                        or (move.origin_returned_move_id and move.to_refund)):
                    qty += move.product_uom._compute_quantity(
                        move.product_uom_qty, self.product_uom_id)
            elif (move.location_dest_id.usage == "customer"
                  and move.to_refund):
                qty -= move.product_uom._compute_quantity(
                    move.product_uom_qty, self.product_uom_id)
        return qty
