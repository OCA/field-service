# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMEquipment(models.Model):
    _inherit = 'fsm.equipment'
    _description = "FSM Equipment Inherits"

    product_id = fields.Many2one(
        'product.product', string='Product', required=True)
    lot_id = fields.Many2one(
        'stock.production.lot', string='Serial #', required=True)
    current_stock_location_id = fields.Many2one(
        'stock.location', string='Current Inventory Location',
        compute='_compute_current_stock_loc_id')

    @api.multi
    def _compute_current_stock_loc_id(self):
        for equipment in self:
            quants = self.env['stock.quant'].search(
                [('lot_id', '=', self.lot_id.id)], order="id desc")
            if quants:
                equipment.current_stock_location_id = \
                    quants[0].location_id.id or False
            else:
                equipment.current_stock_location_id = False
