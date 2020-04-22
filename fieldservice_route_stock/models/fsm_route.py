# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class FsmRoute(models.Model):
    _inherit = 'fsm.route'

    @api.model
    @api.depends('max_product_id', 'fsm_vehicle_id', 'fsm_vehicle_ids')
    def _compute_max_from_vehicles(self):
        for rec in self:
            vehicles = rec.fsm_vehicle_ids + rec.fsm_vehicle_id
            max_qty = 0
            for vehicle in vehicles:
                if vehicle.inventory_location_id:
                    limits = self.env['stock.location.limit'].search([
                        ('location_id', '=', vehicle.inventory_location_id.id),
                        ('product_id', '=', rec.max_product_id.id)
                    ])
                    for limit in limits:
                        max_qty += limit.qty
            rec.max_product_qty = max_qty

    max_product_id = fields.Many2one('product.product', string='Product')
    max_product_uom_id = fields.Many2one(
        'uom.uom', related='max_product_id.uom_id', string='UoM', store=True)
    max_product_qty = fields.Float(
        compute=_compute_max_from_vehicles, string='Maximum Quantity',
        store=True, digits=dp.get_precision('Product Quantity'))
