# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    fsm_order_line_id = fields.Many2one('fsm.order.line', 'FSM Order Line')
    fsm_order_return_line_id = fields.Many2one(
        'fsm.order.return', 'FSM Order Return Line')

    def prepare_equipment_values(self, move_line):
        return {'name': '%s (%s)' % (move_line.product_id.name,
                                     move_line.lot_id.name),
                'product_id': move_line.product_id.id,
                'lot_id': move_line.lot_id.id}

    def _action_done(self):
        res = False
        for rec in self:
            res = super(StockMove, rec)._action_done()
            for line in res.mapped('fsm_order_line_id').sudo():
                line.qty_delivered = line._get_delivered_qty()
            for line in res.mapped('fsm_order_return_line_id').sudo():
                line.qty_received = line._get_received_qty()
            if rec.picking_code == 'outgoing' and rec.state == 'done':
                if rec.product_tmpl_id.create_fsm_equipment:
                    for line in rec.move_line_ids:
                        vals = self.prepare_equipment_values(line)
                        line.lot_id.equipment_id = rec.env['fsm.equipment'].\
                            create(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(StockMove, self).write(vals)
        if 'product_uom_qty' in vals:
            for move in self:
                if move.state == 'done':
                    for line in self.mapped('fsm_order_line_id').sudo():
                        line.qty_delivered = line._get_delivered_qty()
        return res


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    fsm_order_id = fields.Many2one('fsm.order', 'Field Service Order')


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom,
                               location_id, name, origin, values, group_id):
        result = super(ProcurementRule, self)._get_stock_move_values(
            product_id, product_qty, product_uom,
            location_id, name, origin, values, group_id)
        if values.get('fsm_order_line_id', False):
            result['fsm_order_line_id'] = values['fsm_order_line_id']
        if values.get('fsm_order_return_line_id', False):
            result['fsm_order_return_line_id'] = \
                values['fsm_order_return_line_id']
        return result


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    fsm_order_id = fields.Many2one(
        related="group_id.fsm_order_id", string="Field Service Order",
        store=True)


class StockLocationRoute(models.Model):
    _inherit = 'stock.location.route'

    fsm_selectable = fields.Boolean(string="Field Service Order Lines")
    fsm_return_selectable = fields.Boolean(string="Field Service Return Lines")


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    count_fsm_requests = fields.Integer(compute='_compute_fsm_request')

    def _compute_fsm_request(self):
        for ptype in self:
            if ptype.code == 'outgoing':
                res = self.env['fsm.order'].search([('warehouse_id',
                                                     '=',
                                                     ptype.warehouse_id.id),
                                                    ('inventory_stage', '=',
                                                     'requested')])
                for order in res:
                    for line in order.line_ids:
                        if line.state == 'requested':
                            ptype.count_fsm_requests += 1
                            break
            if ptype.code == 'incoming':
                res = self.env['fsm.order'].search([('warehouse_id',
                                                     '=',
                                                     ptype.warehouse_id.id),
                                                    ('inventory_stage', '=',
                                                     'requested')])
                for order in res:
                    for line in order.return_ids:
                        if line.state == 'requested':
                            ptype.count_fsm_requests += 1
                            break

    def get_action_fsm_requests(self):
        return self._get_action('fieldservice_stock.action_stock_fsm_order')
