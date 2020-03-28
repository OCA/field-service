# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    fsm_vehicle_id = fields.Many2one('fsm.vehicle', string='Vehicle')

    @api.multi
    def action_assign(self):
        res = {}
        for rec in self:
            if rec.picking_type_id in (
                # Vehicle Loading
                self.env.ref(
                    'fieldservice_vehicle_stock.'
                    'picking_type_output_to_vehicle'),
                # Location Pickup
                self.env.ref(
                    'fieldservice_vehicle_stock.'
                    'picking_type_location_to_vehicle')
            ):
                if rec.fsm_vehicle_id:
                    picking = \
                        rec.with_context(vehicle_id=rec.fsm_vehicle_id.id)
                    res = super(StockPicking, picking).action_assign()
                else:
                    raise UserError(_(
                        "You must provide the vehicle for this picking type."))
            res = super(StockPicking, rec).action_assign()
        return res

    def prepare_fsm_values(self, fsm_order):
        res = {}
        if fsm_order:
            res.update({
                'fsm_vehicle_id': fsm_order.vehicle_id.id or False,
            })
        return res

    @api.multi
    def write(self, vals):
        if vals.get('fsm_order_id', False):
            fsm_order = self.env['fsm.order'].browse(vals.get('fsm_order_id'))
            vals.update(self.prepare_fsm_values(fsm_order))
        return super().write(vals)
