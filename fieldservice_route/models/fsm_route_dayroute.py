# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent consulting Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FSMRouteDayRoute(models.Model):
    _name = 'fsm.route.dayroute'
    _description = 'Field Service Route Dayroute'

    @api.model
    def _get_default_person(self):
        return self.route_id.fsm_person_id.id or False

    @api.model
    def _get_default_date_start_planned(self):
        if self.date:
            return datetime.combine(
                # TODO: Use the worker timezone and working schedule
                self.date, datetime.strptime("8:00:01", '%H:%M:%S').time())

    @api.depends('route_id')
    def _compute_order_count(self):
        for rec in self:
            rec.order_count = 0
            if rec.order_ids:
                rec.order_count = len(rec.order_ids)

    name = fields.Char(string='Name', required=True,
                       default=lambda self: _('New'))
    person_id = fields.Many2one('fsm.person', string='Person',
                                default=_get_default_person)
    route_id = fields.Many2one('fsm.route', string='Route')
    date = fields.Date(string='Date', required=True)
    team_id = fields.Many2one('fsm.team', string='Team')
    stage_id = fields.Many2one('fsm.stage', string='Stage',
                               domain="[('stage_type', '=', 'route')]",
                               index=True, copy=False,
                               default=lambda self: self._default_stage_id())
    territory_id = fields.Many2one(
        'fsm.territory', related='route_id.territory_id', string='Territory')
    longitude = fields.Float("Longitude")
    latitude = fields.Float("Latitude")
    last_location_id = fields.Many2one('fsm.location', string='Last Location')
    date_start_planned = fields.Datetime(
        string='Planned Start Time',
        default=_get_default_date_start_planned)
    start_location_id = fields.Many2one(
        'fsm.location', string='Start Location')
    end_location_id = fields.Many2one('fsm.location', string='End Location')
    work_time = fields.Float(string='Time before overtime (in hours)',
                             default=8.0)
    max_allow_time = fields.Float(string="Maximal Allowable Time (in hours)",
                                  default=10.0)
    order_ids = fields.One2many('fsm.order', 'dayroute_id',
                                string='Orders')
    order_count = fields.Integer(string='Number of Orders',
                                 compute=_compute_order_count)
    order_max = fields.Integer(
        related='route_id.max_order', string="Capacity",
        help="Maximum numbers of orders that can be added to this day route.")

    _sql_constraints = [
        ('fsm_route_dayroute_person_date_uniq',
         'unique (person_id, date)',
         "You cannot create 2 day routes for the same"
         " worker on the same day!"),
    ]

    def _default_stage_id(self):
        return self.env['fsm.stage'].search([('stage_type', '=', 'route'),
                                             ('is_default', '=', True)],
                                            limit=1)

    @api.onchange('route_id')
    def _onchange_person(self):
        self.fsm_person_id = self._get_default_person()

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'fsm.route.dayroute') or _('New')
        return super().create(vals)

    @api.constrains('date', 'route_id')
    def check_day(self):
        for rec in self:
            if rec.date and rec.route_id:
                # Get the day of the week: Monday -> 0, Sunday -> 6
                day_index = rec.date.weekday()
                day = self.env.ref(
                    'fieldservice_route.fsm_route_day_' + str(day_index))
                if day.id not in rec.route_id.day_ids.ids:
                    raise ValidationError(_(
                        "The route %s does not run on %s!" %
                        (rec.route_id.name, day.name)))

    @api.constrains('order_max', 'order_count')
    def check_capacity(self):
        for rec in self:
            if rec.order_count > rec.order_max:
                raise ValidationError(_(
                    "The day route is exceeding the maximum number of "
                    "orders of the route."))
