# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from odoo import api, fields, _
from . import fsm_stage

from odoo.addons.base_geoengine import geo_model
from odoo.addons.base_geoengine import fields as geo_fields


class FSMOrder(geo_model.GeoModel):
    _name = 'fsm.order'
    _description = 'Field Service Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_stage_id(self):
        return self.env.ref('fieldservice.fsm_stage_new')

    @api.depends('date_start', 'date_end')
    def _compute_duration(self):
        if self.date_start and self.date_end:
            start = fields.Datetime.from_string(self.date_start)
            end = fields.Datetime.from_string(self.date_end)
            delta = end - start
            self.duration = delta.total_seconds() / 3600

    @api.depends('stage_id')
    def _get_stage_color(self):
        """ Get stage color"""
        self.custom_color = self.stage_id.custom_color or '#FFFFFF'

    stage_id = fields.Many2one('fsm.stage', string='Stage',
                               track_visibility='onchange',
                               index=True,
                               group_expand='_read_group_stage_ids',
                               default=lambda self: self._default_stage_id())
    priority = fields.Selection(fsm_stage.AVAILABLE_PRIORITIES,
                                string='Priority',
                                index=True,
                                default=fsm_stage.AVAILABLE_PRIORITIES[0][0])
    tag_ids = fields.Many2many('fsm.tag', 'fsm_order_tag_rel',
                               'fsm_order_id',
                               'tag_id', string='Tags',
                               help="Classify and analyze your orders")
    color = fields.Integer('Color Index', default=0)

    # Request
    name = fields.Char(string='Name', required=True, index=True, copy=False,
                       default=lambda self: _('New'))
    customer_id = fields.Many2one('res.partner', string='Customer',
                                  domain=[('customer', '=', True)],
                                  change_default=True,
                                  index=True,
                                  track_visibility='always')
    location_id = fields.Many2one('fsm.location', string='Location',
                                  index=True)
    request_early = fields.Datetime(string='Earliest Request Date')
    request_late = fields.Datetime(string='Latest Request Date')

    description = fields.Text(string='Description')

    person_ids = fields.Many2many('fsm.person', string='Field Service Workers')

    # Planning
    person_id = fields.Many2one('fsm.person', string='Assigned To',
                                index=True)
    route_id = fields.Many2one('fsm.route', string='Route', index=True)
    scheduled_date_start = fields.Datetime(string='Scheduled Start (ETA)')
    scheduled_duration = fields.Float(string='Scheduled duration',
                                      help='Scheduled duration of the work in'
                                           ' hours')
    scheduled_date_end = fields.Datetime(string="Scheduled End")
    sequence = fields.Integer(string='Sequence', default=10)
    todo = fields.Text(string='Instructions')

    # Execution
    log = fields.Text(string='Log')
    date_start = fields.Datetime(string='Actual Start')
    date_end = fields.Datetime(string='Actual End')
    duration = fields.Float(string='Actual duration',
                            compute=_compute_duration,
                            help='Actual duration in hours')

    # Location
    branch_id = fields.Many2one('fsm.branch', string='Branch')
    district_id = fields.Many2one('fsm.district', string='District')
    region_id = fields.Many2one('fsm.region', string='Region')

    # Geometry Field
    shape = geo_fields.GeoPoint(string='Coordinate')

    # Fields for Geoengine Identify
    display_name = fields.Char(related="name", string="Order")
    street = fields.Char(related="location_id.street")
    street2 = fields.Char(related="location_id.street2")
    zip = fields.Char(related="location_id.zip")
    city = fields.Char(related="location_id.city")
    state_name = fields.Char(related="location_id.state_id.name",
                             string='State', ondelete='restrict')
    country_name = fields.Char(related="location_id.country_id.name",
                               string='Country', ondelete='restrict')
    phone = fields.Char(related="location_id.phone")
    mobile = fields.Char(related="location_id.mobile")

    stage_name = fields.Char(related="stage_id.name", string="Stage")
    # Field for Stage Color
    custom_color = fields.Char(related="stage_id.custom_color",
                               string='Stage Color')

    # Template
    template_id = fields.Many2one('fsm.template', string="Template")
    category_ids = fields.Many2many('fsm.category', string="Categories")

    # Equipment
    equipment_id = fields.Many2one('fsm.equipment', string='Equipment')
    type = fields.Selection([], string='Type')

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['fsm.stage'].search([])
        return stage_ids

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fsm.order') \
                or _('New')
        if vals['request_early'] is not False and\
                vals['scheduled_date_start'] is False:
            req_date = fields.Datetime.from_string(vals['request_early'])
            # Round scheduled date start
            req_date = req_date.replace(minute=0, second=0)
            vals.update({'scheduled_date_start': str(req_date),
                         'request_early': str(req_date)})
        return super(FSMOrder, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'scheduled_date_end' in vals:
            date_to_with_delta = fields.Datetime.from_string(
                vals.get('scheduled_date_end')) - \
                timedelta(hours=self.scheduled_duration)
            vals['scheduled_date_start'] = str(date_to_with_delta)
        if 'scheduled_duration' in vals:
            date_to_with_delta = fields.Datetime.from_string(
                vals.get('scheduled_date_start', self.scheduled_date_start))\
                + timedelta(hours=vals.get('scheduled_duration'))
            vals['scheduled_date_end'] = str(date_to_with_delta)
        if 'scheduled_date_end' not in vals and 'scheduled_date_start' in vals:
            date_to_with_delta = fields.Datetime.from_string(
                vals.get('scheduled_date_start')) + \
                timedelta(hours=self.scheduled_duration)
            vals['scheduled_date_end'] = str(date_to_with_delta)
        return super(FSMOrder, self).write(vals)

    def action_confirm(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_confirmed').id})

    def action_request(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_requested').id})

    def action_assign(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_assigned').id})

    def action_schedule(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_scheduled').id})

    def action_enroute(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_enroute').id})

    def action_start(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_started').id})

    def action_complete(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_completed').id})

    def action_cancel(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_cancelled').id})

    @api.onchange('scheduled_date_end')
    def onchange_scheduled_date_end(self):
        if self.scheduled_date_end:
            date_to_with_delta = fields.Datetime.from_string(
                self.scheduled_date_end) - \
                timedelta(hours=self.scheduled_duration)
            self.date_start = str(date_to_with_delta)

    @api.onchange('scheduled_duration')
    def onchange_scheduled_duration(self):
        if self.scheduled_duration:
            date_to_with_delta = fields.Datetime.from_string(
                self.scheduled_date_start) + \
                timedelta(hours=self.scheduled_duration)
            self.scheduled_date_end = str(date_to_with_delta)

    @api.onchange('location_id')
    def onchange_location_id(self):
        if self.location_id:
            self.branch_id = self.location_id.branch_id or False
            self.district_id = self.location_id.district_id or False
            self.region_id = self.location_id.region_id or False

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            self.category_ids = self.template_id.category_ids

    def geo_localize(self):
        for order in self:
            if order.location_id.partner_id:
                order.location_id.partner_id.geo_localize()
            lat = order.location_id.partner_latitude
            lng = order.location_id.partner_longitude
            point = geo_fields.GeoPoint.from_latlon(cr=order.env.cr,
                                                    latitude=lat,
                                                    longitude=lng)
            order.shape = point
