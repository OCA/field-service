# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FSMRouteDayRoute(models.Model):
    _inherit = 'fsm.route.dayroute'

    @api.depends('order_ids.move_ids', 'route_id', 'max_product_qty')
    def _compute_product_qty(self):
        for rec in self:
            product_qty = 0.00
            if rec.order_ids and rec.max_product_id:
                for order in rec.order_ids:
                    for move in order.move_ids:
                        # If the product is the product used for the capacity
                        # or one of his equivalents, count it
                        equiv_ids = rec.max_product_id.product_tmpl_id.\
                            equivalent_product_ids.ids
                        equiv_ids.append(rec.max_product_id.product_tmpl_id.id)
                        if move.product_id.product_tmpl_id.id in equiv_ids:
                            product_qty += move.product_uom_qty
            rec.product_qty = product_qty
            rec.product_qty_remaining = rec.max_product_qty - product_qty

    @api.depends('fsm_vehicle_id', 'route_id')
    def _compute_vehicle_capacity(self):
        for rec in self:
            is_limited = False
            max_qty = 0.00
            if rec.fsm_vehicle_id and rec.route_id:
                limit = self.env['stock.location.limit'].search([
                    ('location_id', '=',
                     rec.fsm_vehicle_id.inventory_location_id.id),
                    ('product_id', '=', rec.route_id.max_product_id.id)
                ])
                if limit:
                    is_limited = True
                    max_qty = limit.qty
            rec.is_limited = is_limited
            rec.max_product_qty = max_qty

    final_inventory_id = fields.Many2one(
        'stock.inventory', string='Final Inventory')
    inventory_location_id = fields.Many2one(
        related='fsm_vehicle_id.inventory_location_id')
    adjustment_invoice_id = fields.Many2one(
        'account.invoice', string='Adjustment Invoice')
    product_qty = fields.Float(
        compute=_compute_product_qty, string="Product Quantity", store=True)
    product_qty_remaining = fields.Float(
        compute=_compute_product_qty, string="Available Stock Capacity",
        store=True)
    is_limited = fields.Boolean(
        compute=_compute_vehicle_capacity, string="Is Limited?", store=True)
    max_product_id = fields.Many2one(
        'product.product', related='route_id.max_product_id', store=True)
    max_product_qty = fields.Float(
        compute='_compute_vehicle_capacity',
        string="Maximum Stock Capacity",
        help="Maximum quantity of product that the vehicle can carry.")
    picking_count = fields.Integer(
        compute='_compute_picking_count', string='Transfers')
    batch_picking_id = fields.Many2one(
        "stock.picking.batch", string="Batch Picking")

    @api.multi
    @api.constrains('is_limited', 'product_qty_remaining')
    def check_vehicle_capacity(self):
        for rec in self:
            if rec.is_limited and rec.product_qty_remaining < 0:
                raise ValidationError(_(
                    "The vehicle %s is over capacity (%s > %s) on %s." %
                    (rec.fsm_vehicle_id.name, rec.product_qty,
                     rec.max_product_qty, rec.date)))

    @api.multi
    def write(self, vals):
        Stage = self.env['fsm.stage']
        Invoice = self.env['account.invoice']
        for rec in self:
            if vals.get('stage_id', False):
                stage = Stage.browse(vals.get('stage_id'))
                if (stage.is_closed and stage.stage_type == 'route' and
                        rec.final_inventory_id.state == 'done'):
                    partner = rec.person_id.partner_id.commercial_partner_id
                    lines = []
                    moves = rec.final_inventory_id.move_ids.filtered(
                        lambda x:
                        x.location_id.id == rec.inventory_location_id.id)
                    if moves:
                        for move in moves:
                            account = \
                                move.product_id.property_account_income_id or\
                                move.product_id.categ_id.\
                                    property_account_income_categ_id
                            lines.append((0, 0, {
                                'name': move.product_id.name,
                                'product_id': move.product_id.id,
                                'account_id': account.id,
                                'quantity': move.product_uom_qty,
                                'uom_id': move.product_uom.id,
                                'price_unit': move.product_id.list_price
                            }))
                        invoice_vals = {
                            'name': rec.name,
                            'partner_id': partner.id,
                            'date_invoice': rec.date,
                            'type': 'out_invoice',
                            'journal_id':
                                self.env['account.journal'].search([
                                    ('type', '=', 'sale'),
                                ], limit=1).id,
                            'invoice_line_ids': lines,
                        }
                        invoice = Invoice.create(invoice_vals)
                        vals.update({'adjustment_invoice_id': invoice.id})
        return super().write(vals)

    @api.depends('order_ids')
    def _compute_picking_count(self):
        for dayroute in self:
            for order in dayroute.order_ids:
                dayroute.picking_count += len(order.picking_ids)

    @api.multi
    def action_view_picking(self):
        action = self.env.ref(
            'stock.action_picking_tree_all').read()[0]
        picking_ids = []
        for order in self.order_ids:
            for picking in order.picking_ids:
                picking_ids.append(picking.id)
        if self.picking_count > 1:
            action['domain'] = [('id', 'in', picking_ids)]
        elif self.picking_count == 1:
            action['views'] = \
                [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = picking_ids[0]
        return action
