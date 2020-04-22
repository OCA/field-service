# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class FSMRouteDayRoute(models.Model):
    _inherit = 'fsm.route.dayroute'

    @api.model
    def _get_default_vehicle(self, vals=None):
        vehicle_id = False
        if self.person_id and self.person_id.vehicle_id:
            vehicle_id = self.person_id.vehicle_id.id
        elif self.route_id and self.route_id.fsm_vehicle_id:
            vehicle_id = self.route_id.fsm_vehicle_id.id
        elif vals and vals.get('route_id', False):
            route = self.env['fsm.route'].browse(vals.get('route_id'))
            vehicle_id = route.fsm_vehicle_id and \
                route.fsm_vehicle_id.id or False
        return vehicle_id

    fsm_vehicle_id = fields.Many2one(
        'fsm.vehicle', string='Vehicle', index=True,
        default=_get_default_vehicle)

    @api.onchange('route_id')
    def _onchange_route_id(self):
        self.fsm_vehicle_id = self._get_default_vehicle()

    @api.multi
    def assign_vehicle_to_pickings(self):
        for rec in self:
            for order in rec.order_ids:
                order.assign_vehicle_to_pickings()

    @api.model
    def create(self, vals):
        if not vals.get('fsm_vehicle_id', False):
            vals.update({
                'fsm_vehicle_id': self._get_default_vehicle(vals),
            })
        res = super().create(vals)
        res.assign_vehicle_to_pickings()
        return res

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if vals.get('fsm_vehicle_id', False) and self.order_ids:
            for order in self.order_ids:
                order.vehicle_id = vals.get('fsm_vehicle_id')
        self.assign_vehicle_to_pickings()
        return res
