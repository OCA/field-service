# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockRequest(models.Model):
    _inherit = "stock.request"

    fsm_order_id = fields.Many2one(
        'fsm.order', string="FSM Order", ondelete='cascade',
        index=True, copy=False)
    direction = fields.Selection([('outbound', 'Outbound'),
                                  ('inbound', 'Inbound')], string='Direction')

    @api.onchange('direction')
    def onchange_direction(self):
        """To set route based on direction."""
        route_ids = False
        if self.direction == 'outbound':
            route_ids = self.env['stock.location.route'].search(
                [('fsm_selectable', '=', True)])
        if self.direction == 'inbound':
            route_ids = self.env['stock.location.route'].search(
                [('fsm_return_selectable', '=', True)])
        return {'domain': {'route_id': [('id', 'in',
                                         route_ids and route_ids.ids or [])]}}


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _action_done(self):
        res = super(StockMoveLine, self)._action_done()
        for rec in self:
            for all_rec in rec.move_id.allocation_ids:
                request = all_rec.stock_request_id
                if request.state == 'done' and request.fsm_order_id:
                    request.fsm_order_id.request_stage = 'done'
        return res


class StockMove(models.Model):
    _inherit = "stock.move"

    def prepare_equipment_values(self, move_line):
        return {'name': '%s (%s)' % (
            move_line.product_id.name, move_line.lot_id.name),
            'product_id': move_line.product_id.id,
            'lot_id': move_line.lot_id.id,
            'current_location_id':
            move_line.request_id.fsm_order_id.location_id.id,
            'current_stock_location_id': move_line.dest_location_id.id}

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
                res = self.env['fsm.order'].search(
                    [('request_stage', '=', 'draft'),
                     ('warehouse_id', '=', ptype.warehouse_id.id)])
                ptype.count_fsm_requests = len(res)
            if ptype.code == 'incoming':
                res = self.env['fsm.order'].search(
                    [('request_stage', '=', 'draft'),
                     ('warehouse_id', '=', ptype.warehouse_id.id)])
                ptype.count_fsm_requests = len(res)

    def get_action_fsm_requests(self):
        return self._get_action('fieldservice_stock.action_stock_fsm_order')
