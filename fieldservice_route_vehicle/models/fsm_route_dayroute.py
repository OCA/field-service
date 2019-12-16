# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMRouteDayRoute(models.Model):
    _inherit = 'fsm.route.dayroute'

    fsm_vehicle_id = fields.Many2one('fsm.vehicle',
                                     string='Vehicle')

    @api.onchange('route_id')
    def _onchange_route_id(self):
        self.fsm_vehicle_id = self.route_id and \
            self.route_id.fsm_vehicle_id or False
