# Copyright (C) 2018 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def prepare_equipment_values(self, move_line):
        return {'name': '%s (%s)' % (
            move_line.product_id.name, move_line.lot_id.name),
            'product_id': move_line.product_id.id,
            'lot_id': move_line.lot_id.id,
            'location_id':
            move_line.move_id.stock_request_ids.fsm_order_id.location_id.id,
            'current_location_id':
            move_line.move_id.stock_request_ids.fsm_order_id.location_id.id,
            'current_stock_location_id': move_line.location_dest_id.id}

    def _action_done(self):
        res = super()._action_done()
        for rec in self:
            if (rec.state == 'done'
                    and rec.picking_type_id.create_fsm_equipment
                    and rec.product_tmpl_id.create_fsm_equipment):
                for line in rec.move_line_ids:
                    vals = self.prepare_equipment_values(line)
                    line.lot_id.fsm_equipment_id = \
                        rec.env['fsm.equipment'].create(vals)
        return res
