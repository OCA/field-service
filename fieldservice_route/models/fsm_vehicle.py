# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class FSMVehicle(models.Model):
    _inherit = 'fsm.vehicle'

    @api.model
    def create(self, vals):
        vehicle = super(FSMVehicle, self).create(vals)
        if vehicle.person_id:
            fsm_person_ids = self.env['fsm.person'].search([
                ('vehicle_id', '=', vehicle.id)])
            for person in fsm_person_ids:
                person.vehicle_id = False
            vehicle.person_id.vehicle_id = vehicle.id
        return vehicle

    @api.multi
    def write(self, vals):
        res = super(FSMVehicle, self).write(vals)
        for vehicle_rec in self:
            if vals.get('person_id'):
                fsm_person_ids = self.env['fsm.person'].search([
                    ('vehicle_id', '=', vehicle_rec.id)])
                for person in fsm_person_ids:
                    person.vehicle_id = False
                vehicle_rec.person_id.vehicle_id = vehicle_rec.id
        return res
