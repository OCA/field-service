# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    start_time = fields.Float(string='Start Time')
    start_location = fields.Char(string='Start Location')
    end_location = fields.Char(string='End Location')
    time_before_overtime = fields.Float(
        string='Time Before Overtime', default=8.0)
    maximal_allowable_time = fields.Float(
        string='Maximal Allowable Time', default=10.0)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(start_time=self.env['ir.config_parameter'].sudo().
                   get_param('fieldservice_route.start_time'))
        res.update(start_location=self.env['ir.config_parameter'].sudo().
                   get_param('fieldservice_route.start_location'))
        res.update(end_location=self.env['ir.config_parameter'].sudo().
                   get_param('fieldservice_route.end_location'))
        res.update(time_before_overtime=self.env['ir.config_parameter'].sudo().
                   get_param('fieldservice_route.time_before_overtime'))
        res.update(maximal_allowable_time=self.env[
            'ir.config_parameter'].sudo().get_param(
            'fieldservice_route.maximal_allowable_time'))
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            "fieldservice_route.start_time",
            self.start_time)
        self.env['ir.config_parameter'].sudo().set_param(
            "fieldservice_route.start_location",
            self.start_location)
        self.env['ir.config_parameter'].sudo().set_param(
            "fieldservice_route.end_location",
            self.end_location)
        self.env['ir.config_parameter'].sudo().set_param(
            "fieldservice_route.time_before_overtime",
            self.time_before_overtime)
        self.env['ir.config_parameter'].sudo().set_param(
            "fieldservice_route.maximal_allowable_time",
            self.maximal_allowable_time)
        return res
