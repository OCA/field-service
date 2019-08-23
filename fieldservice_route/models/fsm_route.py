# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMRoute(models.Model):
    _inherit = 'fsm.route'

    fsm_team_id = fields.Many2one('fsm.team', string='FSM Team')
    stage_id = fields.Many2one('fsm.stage', string='Status',
                               domain="[('stage_type', '=', 'route')]")
    territory_ids = fields.Many2many('fsm.territory', string='Territories')
    lat = fields.Char(string='Latitude')
    long = fields.Char(string='Longitude')
    location_id = fields.Many2one('fsm.location',
                                  string='Last known FSM Location')
    planned_start_time = fields.Float(string='Planned Start time')
    start_location = fields.Char(string='Start Location')
    end_location = fields.Char(string='End Location')
    time_before_overtime = fields.Float(string='Time Before Overtime')
    maximal_allowable_time = fields.Float(string='Maximal Allowable Time')
    number_of_orders = fields.Integer(string='Number Of Orders',
                                      compute='_compute_order_ids')
    scheduled_date = fields.Date(string='Scheduled Date')
    capacity = fields.Float(string='Capacity', compute='_compute_order_ids')

    @api.depends('order_ids', 'maximal_allowable_time')
    def _compute_order_ids(self):
        for route_rec in self:
            if route_rec.maximal_allowable_time:
                route_rec.capacity = sum(route_rec.order_ids.mapped(
                    'scheduled_duration')) / route_rec.maximal_allowable_time
            route_rec.number_of_orders = len(route_rec.order_ids.ids)

    @api.model
    def default_get(self, fields):
        result = super(FSMRoute, self).default_get(fields)
        ir_config_param_obj = self.env['ir.config_parameter']
        result['planned_start_time'] =\
            ir_config_param_obj.sudo().get_param(
                'fieldservice_route.start_time')
        result['start_location'] =\
            ir_config_param_obj.sudo().get_param(
                'fieldservice_route.start_location')
        result['end_location'] =\
            ir_config_param_obj.sudo().get_param(
                'fieldservice_route.end_location')
        result['maximal_allowable_time'] =\
            ir_config_param_obj.sudo().get_param(
                'fieldservice_route.maximal_allowable_time')
        result['time_before_overtime'] = \
            ir_config_param_obj.sudo().get_param(
                'fieldservice_route.time_before_overtime')
        return result

    @api.onchange('person_id')
    def _onchange_person_id(self):
        if self.person_id:
            self.territory_ids = [(6, 0, self.person_id.territory_ids.ids)]
