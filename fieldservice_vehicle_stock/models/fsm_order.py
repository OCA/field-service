# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    @api.multi
    def assign_vehicle_to_pickings(self):
        for rec in self:
            for picking in rec.picking_ids:
                if picking.state in ('waiting', 'confirmed', 'assigned'):
                    picking.fsm_vehicle_id = self.vehicle_id.id or False

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if vals.get('vehicle_id', False):
                rec.assign_vehicle_to_pickings()
        return res
