# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _action_done(self):
        res = super(StockMoveLine, self)._action_done()
        for rec in self:
            if rec.move_id and rec.move_id.allocation_ids:
                for request in rec.move_id.allocation_ids:
                    if (request.stock_request_id.state == 'done'
                            and request.stock_request_id.fsm_order_id):
                        request.stock_request_id.\
                            fsm_order_id.request_stage = 'done'
        return res


class StockMove(models.Model):
    _inherit = "stock.move"

    fsm_order_id = fields.Many2one('fsm.order', string='Field Service Order')

    def prepare_equipment_values(self, move_line):
        return {'name': '%s (%s)' % (
            move_line.product_id.name, move_line.lot_id.name),
            'product_id': move_line.product_id.id,
            'lot_id': move_line.lot_id.id,
            'current_location_id':
            move_line.move_id.stock_request_ids.fsm_order_id.location_id.id,
            'current_stock_location_id': move_line.location_dest_id.id}

    def _action_done(self):
        res = False
        for rec in self:
            res = super(StockMove, rec)._action_done()
            if rec.picking_code == 'outgoing' and rec.state == 'done':
                if rec.product_tmpl_id.create_fsm_equipment:
                    for line in rec.move_line_ids:
                        vals = self.prepare_equipment_values(line)
                        line.lot_id.fsm_equipment_id = \
                            rec.env['fsm.equipment'].create(vals)
        return res


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    fsm_order_id = fields.Many2one('fsm.order', 'Field Service Order')


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom,
                               location_id, name, origin, values, group_id):
        vals = super()._get_stock_move_values(
            product_id, product_qty, product_uom, location_id, name, origin,
            values, group_id)
        vals.update({
            'fsm_order_id': values.get('fsm_order_id'),
        })
        return vals


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    fsm_order_id = fields.Many2one(
        related="group_id.fsm_order_id", string="Field Service Order",
        store=True)
