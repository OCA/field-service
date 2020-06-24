# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    repair_id = fields.Many2one('repair.order', string='Repair Order')

    @api.model
    def create(self, vals):
        # if FSM order with type repair is created then
        # create a repair order
        order = super(FSMOrder, self).create(vals)
        if order.type.internal_type == 'repair':
            if (order.equipment_id and
                    order.equipment_id.current_stock_location_id):
                equipment = order.equipment_id
                repair_id = self.env['repair.order'].create({
                    'name': order.name or '',
                    'product_id': equipment.product_id.id or False,
                    'product_uom': equipment.product_id.uom_id.id or False,
                    'location_id':
                        equipment.current_stock_location_id and
                        equipment.current_stock_location_id.id or False,
                    'lot_id': equipment.lot_id.id or '',
                    'product_qty': 1,
                    'invoice_method': 'none',
                    'internal_notes': order.description,
                    'partner_id':
                        order.location_id.partner_id and
                        order.location_id.partner_id.id or False,
                })
                order.repair_id = repair_id
            elif not order.equipment_id.current_stock_location_id:
                raise ValidationError(_("Cannot create Repair Order because "
                                        "Equipment does not have a Current "
                                        "Inventory Location."))
        return order
