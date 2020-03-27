# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class FsmRoute(models.Model):
    _inherit = 'fsm.route'

    @api.model
    def _get_default_vehicle(self):
        return self.fsm_person_id.vehicle_id.id or False

    fsm_vehicle_id = fields.Many2one('fsm.vehicle', string='Main Vehicle',
                                     default=_get_default_vehicle)
    fsm_vehicle_ids = fields.Many2many('fsm.vehicle', string='Vehicles')

    @api.multi
    @api.onchange('fsm_person_id')
    def onchange_vehicle(self):
        for rec in self:
            rec.fsm_vehicle_id = rec._get_default_vehicle()

    @api.constrains('fsm_vehicle_id', 'fsm_vehicle_ids')
    def check_vehicles(self):
        if self.fsm_vehicle_id in self.fsm_vehicle_ids:
            raise UserError(_("The main vehicle doesn't need to be in the "
                              "list of vehicles. Please remove it."))
