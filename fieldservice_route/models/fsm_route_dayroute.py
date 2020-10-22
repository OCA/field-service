# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent consulting Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import pytz
from datetime import datetime, time
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class FSMRouteDayRoute(models.Model):
    _name = 'fsm.route.dayroute'
    _description = 'Field Service Route Dayroute'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    def _default_team_id(self):
        team_ids = self.env['fsm.team'].search([
            ('company_id', 'in', (self.env.user.company_id.id, False))
        ], order='sequence asc', limit=1)
        if team_ids:
            return team_ids[0]
        else:
            raise ValidationError(_(
                "You must create a FSM team first."))

    @api.depends('route_id', 'order_ids')
    def _compute_order_count(self):
        for rec in self:
            rec.order_count = len(rec.order_ids)
            rec.order_remaining = rec.max_order - rec.order_count

    name = fields.Char(string='Name', required=True, copy=False,
                       default=lambda self: _('New'))
    person_id = fields.Many2one('fsm.person', string='Person',
                                track_visibility='onchange')
    route_id = fields.Many2one('fsm.route', string='Route')
    date = fields.Date(string='Date', required=True,
                       track_visibility='onchange')
    team_id = fields.Many2one('fsm.team', string='Team',
                              default=lambda self: self._default_team_id())
    stage_id = fields.Many2one('fsm.stage', string='Stage',
                               domain="[('stage_type', '=', 'route')]",
                               index=True, copy=False,
                               track_visibility='onchange',
                               default=lambda self: self._default_stage_id())
    is_closed = fields.Boolean(related='stage_id.is_closed')
    date_close = fields.Datetime()
    company_id = fields.Many2one(
        'res.company', default=lambda s: s.env.user.company_id)
    territory_id = fields.Many2one(
        'fsm.territory', related='route_id.territory_id', string='Territory')
    longitude = fields.Float("Longitude")
    latitude = fields.Float("Latitude")
    last_location_id = fields.Many2one('fsm.location', string='Last Location')
    date_start_planned = fields.Datetime(string='Planned Start Time')
    start_location_id = fields.Many2one(
        'fsm.location', string='Start Location')
    end_location_id = fields.Many2one('fsm.location', string='End Location')
    work_time = fields.Float(string='Time before overtime (in hours)',
                             default=8.0)
    max_allow_time = fields.Float(string="Maximal Allowable Time (in hours)",
                                  default=10.0)
    order_ids = fields.One2many('fsm.order', 'dayroute_id',
                                string='Orders')
    order_count = fields.Integer(
        compute=_compute_order_count, string='Number of Orders', store=True)
    order_remaining = fields.Integer(
        compute=_compute_order_count, string='Available Capacity', store=True)
    max_order = fields.Integer(
        related='route_id.max_order', string="Maximum Capacity", store=True,
        help="Maximum numbers of orders that can be added to this day route.")

    def _default_stage_id(self):
        return self.env['fsm.stage'].search([('stage_type', '=', 'route'),
                                             ('is_default', '=', True)],
                                            limit=1)

    @api.onchange('route_id')
    def _onchange_person(self):
        self.person_id = self.route_id.fsm_person_id.id

    @api.onchange('date')
    def _onchange_date(self):
        if self.date:
            # TODO: Use the worker timezone and working schedule
            self.date_start_planned = datetime.combine(
                self.date, datetime.strptime("8:00:00", '%H:%M:%S').time())

    @api.multi
    def write(self, values):
        if values.get('stage_id', False) and not \
                self.env.context.get('is_writing_flag', False):
            new_stage = self.env['fsm.stage'].browse(values.get('stage_id'))
            if new_stage.is_closed:
                values.update({'date_close': fields.Datetime.now()})
        return super().write(values)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'fsm.route.dayroute') or _('New')
        if not vals.get('date_start_planned', False) and \
                vals.get('date', False):
            # TODO: Use the worker timezone and working schedule
            date = vals.get('date')
            if type(vals.get('date')) == str:
                date = datetime.strptime(
                    vals.get('date'), DEFAULT_SERVER_DATE_FORMAT).date()
            vals.update({
                'date_start_planned': datetime.combine(
                    date, datetime.strptime("8:00:00", '%H:%M:%S').time())
            })
        return super().create(vals)

    @api.constrains('date', 'route_id')
    def check_day(self):
        for rec in self:
            if rec.date:
                user_tz = self.env.user.tz or pytz.utc
                local = pytz.timezone(user_tz)
                midnight = datetime.combine(rec.date, time())
                utc_midnight = local.localize(midnight).astimezone(pytz.utc)
                holidays = self.env['resource.calendar.leaves'].search([
                    ('date_from', '<=', utc_midnight),
                    ('date_to', '>=', utc_midnight),
                ])
                if holidays:
                    raise ValidationError(_(
                        "%s is a holiday (%s). No route is running." %
                        (rec.date, holidays[0].name)))
                if rec.route_id:
                    run_day = rec.route_id.run_on(rec.date)
                    if not run_day:
                        raise ValidationError(_(
                            "The route %s does not run on %s!" %
                            (rec.route_id.name, rec.date)))

    @api.constrains('route_id', 'max_order', 'order_count')
    def check_capacity(self):
        for rec in self:
            if rec.max_order and rec.order_count > rec.max_order:
                raise ValidationError(_(
                    "The day route is exceeding the maximum number of "
                    "orders of the route."))

    @api.constrains('route_id', 'date')
    def check_max_dayroute(self):
        for rec in self:
            if rec.route_id:
                # TODO: use a single read_group instead of a search in a loop
                dayroutes = self.search([
                    ('route_id', '=', rec.route_id.id),
                    ('date', '=', rec.date),
                ])
                if len(dayroutes) > rec.route_id.max_dayroute:
                    raise ValidationError(_(
                        "The route %s only runs %s time(s) a day." %
                        (rec.route_id.name, rec.route_id.max_dayroute)))

    @api.constrains('stage_id', 'order_ids')
    def check_complete_orders(self):
        for rec in self:
            if rec.stage_id.is_closed:
                if any(order.stage_id.is_closed is False for order in
                       rec.order_ids):
                    raise ValidationError(_(
                        "You must close (complete or cancel) all orders."))
