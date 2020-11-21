# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMEquipment(models.Model):
    _inherit = 'fsm.equipment'

    product_id = fields.Many2one(
        'product.product', string='Product', required=True)
    lot_id = fields.Many2one(
        'stock.production.lot', string='Serial #', required=True)
    current_stock_location_id = fields.Many2one(
        'stock.location', string='Current Inventory Location',
        compute='_compute_current_stock_loc_id')

    @api.depends('product_id', 'lot_id')
    def _compute_current_stock_loc_id(self):
        for equipment in self:
            quants = self.env['stock.quant'].search(
                [('lot_id', '=', equipment.lot_id.id)], order="id desc",
                limit=1)
            if quants and quants.location_id:
                equipment.current_stock_location_id = \
                    quants.location_id.id
            else:
                equipment.current_stock_location_id = False

    @api.onchange('product_id')
    def _onchange_product(self):
        for equipment in self:
            self.current_stock_location_id = False

    @api.model
    def create(self, vals):
        res = super(FSMEquipment, self).create(vals)
        if 'lot_id' in vals:
            res.lot_id.fsm_equipment_id = res.id
        return res

    @api.multi
    def write(self, vals):
        for equipment in self:
            prev_lot = equipment.lot_id
            res = super(FSMEquipment, equipment).write(vals)
            if 'lot_id' in vals:
                prev_lot.fsm_equipment_id = False
                equipment.lot_id.fsm_equipment_id = equipment.id
        return res
