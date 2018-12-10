# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    fsm_order_line_id = fields.Many2one('fsm.order.line', 'FSM Order Line')

    def _action_done(self):
        result = super(StockMove, self)._action_done()
        for line in result.mapped('fsm_order_line_id').sudo():
            line.qty_delivered = line._get_delivered_qty()
        return result

    @api.multi
    def write(self, vals):
        res = super(StockMove, self).write(vals)
        if 'product_uom_qty' in vals:
            for move in self:
                if move.state == 'done':
                    for line in res.mapped('fsm_order_line_id').sudo():
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
        return result


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    fsm_order_id = fields.Many2one(
        related="group_id.fsm_order_id", string="Field Service Order",
        store=True)
