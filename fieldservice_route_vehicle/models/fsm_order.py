# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    def prepare_dayroute_values(self, values):
        res = super().prepare_dayroute_values(values)
        res.update({
            'fsm_vehicle_id': values['vehicle_id']})
        return res

    def _get_dayroute_values(self, vals):
        res = super()._get_dayroute_values(vals)
        res.update({
            'vehicle_id':
                vals.get('vehicle_id') or self.vehicle_id.id or
                self.fsm_route_id.fsm_vehicle_id.id})
        return res

    def _get_dayroute_domain(self, values):
        domain = super()._get_dayroute_domain(values)
        return domain + [('fsm_vehicle_id', '=', values['vehicle_id']),
                         ('product_qty_remaining', '>', 0)]

    @api.model
    def create(self, vals):
        if not vals.get('vehicle_id', False):
            location = self.env['fsm.location'].browse(vals.get('location_id'))
            vals.update({
                'vehicle_id': location.fsm_route_id.fsm_vehicle_id.id})
        return super().create(vals)

    @api.multi
    def write(self, vals):
        for rec in self:
            if vals.get('vehicle_id', False):
                vals = rec._manage_fsm_route(vals)
        return super().write(vals)
