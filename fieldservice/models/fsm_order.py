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
    name = fields.Char(string='Name', required=True,
                       default=lambda self: _('New'))
    customer_id = fields.Many2one('res.partner', string='Customer',
                                  domain=[('customer', '=', True)],
                                  change_default=True,
                                  index=True,
                                  track_visibility='always')
    fsm_location_id = fields.Many2one('fsm.location', string='Location',
                                      index=True)
    requested_date = fields.Datetime(string='Requested Date')
    description = fields.Text(string='Description')
    origin = fields.Char(string='Origin')

    # Planning
    fsm_person_id = fields.Many2one('fsm.person',
                                    string='Assigned To',
                                    index=True)
    fsm_route_id = fields.Many2one('fsm.route', string='Route', index=True)
    scheduled_date_start = fields.Datetime(string='Scheduled Start')
    scheduled_duration = fields.Float(string='Duration in hours',
                                      help='Scheduled duration of the work in'
                                           ' hours')
    scheduled_date_end = fields.Datetime(string="Scheduled End")
    sequence = fields.Integer(string='Sequence', default=10)
    todo = fields.Text(string='Instructions')

    # Execution
    log = fields.Text(string='Log')
    date_start = fields.Datetime(string='Actual Start')
    date_end = fields.Datetime(string='Actual End')

    # Location
    branch_id = fields.Many2one('branch', string='Branch')
    district_id = fields.Many2one('district', string='District')
    region_id = fields.Many2one('region', string='Region')

    # Geometry Field
    shape = geo_fields.GeoPoint(string='Coordinate')

    # Fields for Geoengine Identify
    display_name = fields.Char(related="fsm_location_id.display_name",
                               string="Location")
    street = fields.Char(related="fsm_location_id.street")
    street2 = fields.Char(related="fsm_location_id.street2")
    zip = fields.Char(related="fsm_location_id.zip")
    city = fields.Char(related="fsm_location_id.city")
    state_name = fields.Char(related="fsm_location_id.state_id.name",
                             string='State', ondelete='restrict')
    country_name = fields.Char(related="fsm_location_id.country_id.name",
                               string='Country', ondelete='restrict')
    phone = fields.Char(related="fsm_location_id.phone")
    mobile = fields.Char(related="fsm_location_id.mobile")

    stage_name = fields.Char(related="stage_id.name", string="Stage")

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['fsm.stage'].search([])
        return stage_ids

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fsm.order') \
                or _('New')
        return super(FSMOrder, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'scheduled_date_end' in vals:
            date_to_with_delta = fields.Datetime.from_string(
                vals.get('scheduled_date_end')) -\
                timedelta(hours=self.scheduled_duration)
            vals['scheduled_date_start'] = str(date_to_with_delta)
        if 'scheduled_duration' in vals:
            date_to_with_delta = fields.Datetime.from_string(
                vals.get('scheduled_date_start', self.scheduled_date_start)) +\
                timedelta(hours=vals.get('scheduled_duration'))
            vals['scheduled_date_end'] = str(date_to_with_delta)
        if 'scheduled_date_end' not in vals and 'scheduled_date_start' in vals:
            date_to_with_delta = fields.Datetime.from_string(
                vals.get('scheduled_date_start')) +\
                timedelta(hours=self.scheduled_duration)
            vals['scheduled_date_end'] = str(date_to_with_delta)
        return super(FSMOrder, self).write(vals)

    def action_confirm(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_confirmed').id})

    def action_schedule(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_scheduled').id})

    def action_assign(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_assigned').id})

    def action_plan(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_planned').id})

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
                self.scheduled_date_end) -\
                timedelta(hours=self.scheduled_duration)
            self.date_start = str(date_to_with_delta)

    @api.onchange('scheduled_duration')
    def onchange_scheduled_duration(self):
        if self.scheduled_duration:
            date_to_with_delta = fields.Datetime.from_string(
                self.scheduled_date_start) +\
                timedelta(hours=self.scheduled_duration)
            self.scheduled_date_end = str(date_to_with_delta)

    @api.onchange('fsm_location_id')
    def onchange_fsm_location_id(self):
        if self.fsm_location_id:
            self.branch_id = self.fsm_location_id.branch_id or False
            self.district_id = self.fsm_location_id.district_id or False
            self.region_id = self.fsm_location_id.region_id or False

    def geo_localize(self):
        for order in self:
            if order.fsm_location_id.partner_id:
                order.fsm_location_id.partner_id.geo_localize()
            lat = order.fsm_location_id.partner_latitude
            lng = order.fsm_location_id.partner_longitude
            point = geo_fields.GeoPoint.from_latlon(cr=order.env.cr,
                                                    latitude=lat,
                                                    longitude=lng)
            order.shape = point
