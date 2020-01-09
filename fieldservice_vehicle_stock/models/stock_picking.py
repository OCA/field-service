# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    fsm_vehicle_id = fields.Many2one('fsm.vehicle', string='Vehicle')

    def action_assign(self):
        if self.picking_type_id in (
            # Vehicle Loading
            self.env.ref(
                'fieldservice_vehicle_stock.picking_type_output_to_vehicle'),
            # Location Pickup
            self.env.ref(
                'fieldservice_vehicle_stock.picking_type_location_to_vehicle')
        ):
            if self.fsm_vehicle_id:
                picking = self.with_context(vehicle_id=self.fsm_vehicle_id.id)
                return super(StockPicking, picking).action_assign()
            else:
                raise UserError(_(
                    "You must provide the vehicle for this picking type."))
        return super().action_assign()

    @api.multi
    def write(self, vals):
        if vals.get('fsm_order_id', False):
            order = self.env['fsm.order'].browse(vals.get('fsm_order_id'))
            vals.update({
                'fsm_vehicle_id': order.vehicle_id.id or False,
            })
        return super().write(vals)
