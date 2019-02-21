# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields
from odoo.addons.base_geoengine import geo_model


class FSMOrder(geo_model.GeoModel):
    _inherit = 'fsm.order'

    type = fields.Selection(selection_add=[('repair', 'Repair')])
    repair_id = fields.Many2one(
        'mrp.repair', 'Repair Order')

    @api.model
    def create(self, vals):
        # if FSM order with type repair is created then
        # create a repair order
        order = super(FSMOrder, self).create(vals)
        if order.type == 'repair':
            if order.equipment_id:
                equipment = order.equipment_id
                repair_id = self.env['mrp.repair'].create({
                    'name': order.name or '',
                    'product_id': equipment.product_id.id or False,
                    'product_uom': equipment.product_id.uom_id.id or False,
                    'location_id': equipment.current_stock_location_id and
                    equipment.current_stock_location_id.id or False,
                    'location_dest_id': equipment.current_stock_location_id and
                    equipment.current_stock_location_id.id or False,
                    'lot_id': equipment.lot_id and equipment.lot_id.name or '',
                    'product_qty': 1,
                    'invoice_method': 'none',
                    'internal_notes': order.description,
                    'partner_id': order.customer_id and order.customer_id.id or
                    False,
                })
                order.repair_id = repair_id
        return order
