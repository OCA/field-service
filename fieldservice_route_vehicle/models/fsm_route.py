# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class FsmRoute(models.Model):
    _inherit = 'fsm.route'

    @api.model
    def _get_default_vehicle(self):
        return self.fsm_person_id.vehicle_id.id or False

    fsm_vehicle_id = fields.Many2one('fsm.vehicle', string='Vehicle',
                                     default=_get_default_vehicle)

    @api.onchange('fsm_person_id')
    def onchange_vehicle(self):
        self.fsm_vehicle_id = self._get_default_vehicle()
