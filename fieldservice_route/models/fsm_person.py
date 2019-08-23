# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMPerson(models.Model):
    _inherit = 'fsm.person'

    start_time = fields.Float(string='Start Time')
    start_location = fields.Char(string='Start Location')
    end_location = fields.Char(string='End Location')
    time_before_overtime = fields.Float(
        string='Time Before Overtime')
    maximal_allowable_time = fields.Float(
        string='Maximal Allowable Time')
    vehicle_id = fields.Many2one('fsm.vehicle', string='Vehicle')

    @api.model
    def default_get(self, fields):
        result = super(FSMPerson, self).default_get(fields)
        ir_config_param_obj = self.env['ir.config_parameter']
        result['start_time'] = \
            ir_config_param_obj.sudo().get_param(
                'fieldservice_route.start_time')
        result['start_location'] = \
            ir_config_param_obj.sudo().get_param(
                'fieldservice_route.start_location')
        result['end_location'] = \
            ir_config_param_obj.sudo().get_param(
                'fieldservice_route.end_location')
        result['maximal_allowable_time'] = \
            ir_config_param_obj.sudo().get_param(
                'fieldservice_route.maximal_allowable_time')
        result['time_before_overtime'] = \
            ir_config_param_obj.sudo().get_param(
                'fieldservice_route.time_before_overtime')
        return result
