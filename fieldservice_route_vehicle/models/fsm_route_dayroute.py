# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMRouteDayRoute(models.Model):
    _inherit = 'fsm.route.dayroute'

    @api.model
    def _get_default_vehicle(self):
        return self.route_id.fsm_vehicle_id.id or False

    fsm_vehicle_id = fields.Many2one(
        'fsm.vehicle', string='Vehicle', index=True,
        default=_get_default_vehicle)

    @api.onchange('route_id')
    def _onchange_route_id(self):
        self.fsm_vehicle_id = self.route_id and \
            self.route_id.fsm_vehicle_id or False

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if vals.get('vehicle_id', False):
            for order in self.order_ids:
                for picking in order.picking_ids:
                    if picking.state in ('waiting', 'confirmed'):
                        picking.vehicle_id = vals.get('vehicle_id')
                        # Set the vehicle on the previous picking as well
                        if picking.move_line_ids[0].move_orig_ids[0]:
                            picking.move_line_ids[0].move_orig_ids[0].\
                                picking_id.vehicle_id = vals.get('vehicle_id')
        return res
