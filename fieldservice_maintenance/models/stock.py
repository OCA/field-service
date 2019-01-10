# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def prepare_equipment_values(self, move_line):
        res = super(StockMove, self).prepare_equipment_values(move_line)
        vals = {'name': '%s (%s)' % (move_line.product_id.name,
                                     move_line.lot_id.name),
                'serial_no': move_line.lot_id.name,
                'is_fsm_equipment': True}
        equipment_id = self.env['maintenance.equipment'].create(vals)
        res.update({'maintenance_equipment_id': equipment_id.id})
        return res
