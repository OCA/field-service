# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from odoo import api, fields, models, _
from . import fsm_stage
from odoo.exceptions import ValidationError


class FSMOrder(models.Model):
    _name = 'fsm.order'
    _description = 'Field Service Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_stage_id(self):
        return self.env.ref('fieldservice.fsm_stage_new')

    def _default_team_id(self):
        return self.env.ref('fieldservice.fsm_team_default')

    @api.depends('date_start', 'date_end')
    def _compute_duration(self):
        for rec in self:
            if rec.date_start and rec.date_end:
                start = fields.Datetime.from_string(rec.date_start)
                end = fields.Datetime.from_string(rec.date_end)
                delta = end - start
                rec.duration = delta.total_seconds() / 3600

    @api.depends('stage_id')
    def _get_stage_color(self):
        """ Get stage color"""
        self.custom_color = self.stage_id.custom_color or '#FFFFFF'

    stage_id = fields.Many2one('fsm.stage', string='Stage',
                               track_visibility='onchange',
                               index=True, copy=False,
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
    team_id = fields.Many2one('fsm.team', string='Team',
                              default=_default_team_id,
                              index=True, required=True,
                              track_visibility='onchange')

    # Request
    name = fields.Char(string='Name', required=True, index=True, copy=False,
                       default=lambda self: _('New'))
    customer_id = fields.Many2one('res.partner', string='Contact',
                                  domain=[('customer', '=', True)],
                                  change_default=True,
                                  index=True,
                                  track_visibility='always')
    location_id = fields.Many2one('fsm.location', string='Location',
                                  index=True, required=True)
    location_directions = fields.Char(string='Location Directions')
    request_early = fields.Datetime(string='Earliest Request Date',
                                    default=datetime.now())
    request_late = fields.Datetime(string='Latest Request Date',
                                   compute='_compute_request_late')
    color = fields.Integer('Color Index')
    company_id = fields.Many2one(
        'res.company', string='Company', required=True, index=True,
        default=lambda self: self.env.user.company_id,
        help="Company related to this order")

    def _compute_request_late(self):
        for rec in self:
            if not rec.request_late:
                if rec.priority == '0':
                    if rec.request_early:
                        rec.request_late = fields.Datetime.from_string(
                            rec.request_early) + timedelta(days=3)
                    else:
                        rec.request_late = datetime.now() + timedelta(days=3)
                elif rec.priority == '1':
                    rec.request_late = fields.Datetime.from_string(
                        rec.request_early) + timedelta(days=2)
                elif rec.priority == '2':
                    rec.request_late = fields.Datetime.from_string(
                        rec.request_early) + timedelta(days=1)
                elif rec.priority == '3':
                    rec.request_late = fields.Datetime.from_string(
                        rec.request_early) + timedelta(hours=8)

    description = fields.Text(string='Description')

    person_ids = fields.Many2many('fsm.person',
                                  string='Field Service Workers')

    @api.onchange('location_id')
    def _onchange_location_id_customer(self):
        if self.company_id.auto_populate_equipments_on_order:
            fsm_equipment_rec = self.env['fsm.equipment'].search([
                ('current_location_id', '=', self.location_id.id)])
            self.equipment_ids = [(6, 0, fsm_equipment_rec.ids)]
        if self.location_id:
            return {'domain': {'customer_id': [('service_location_id', '=',
                                                self.location_id.name)]}}
        else:
            return {'domain': {'customer_id': [('id', '!=', None)]}}

    @api.onchange('customer_id')
    def _onchange_customer_id_location(self):
        if self.customer_id:
            self.location_id = self.customer_id.service_location_id

    # Planning
    person_id = fields.Many2one('fsm.person', string='Assigned To',
                                index=True)
    person_phone = fields.Char(related="person_id.phone",
                               string="Worker Phone")
    route_id = fields.Many2one('fsm.route', string='Route', index=True)
    scheduled_date_start = fields.Datetime(string='Scheduled Start (ETA)')
    scheduled_duration = fields.Float(string='Scheduled duration',
                                      help='Scheduled duration of the work in'
                                           ' hours')
    scheduled_date_end = fields.Datetime(string="Scheduled End")
    sequence = fields.Integer(string='Sequence', default=10)
    todo = fields.Text(string='Instructions')

    # Execution
    resolution = fields.Text(string='Resolution',
                             placeholder="Resolution of the order")
    date_start = fields.Datetime(string='Actual Start')
    date_end = fields.Datetime(string='Actual End')
    duration = fields.Float(string='Actual duration',
                            compute=_compute_duration,
                            help='Actual duration in hours')
    current_date = fields.Datetime(default=fields.datetime.now(), store=True)

    # Location
    territory_id = fields.Many2one('fsm.territory', string="Territory",
                                   related='location_id.territory_id',
                                   store=True)
    branch_id = fields.Many2one('fsm.branch', string='Branch',
                                related='location_id.branch_id',
                                store=True)
    district_id = fields.Many2one('fsm.district', string='District',
                                  related='location_id.district_id',
                                  store=True)
    region_id = fields.Many2one('fsm.region', string='Region',
                                related='location_id.region_id',
                                store=True)

    # Fields for Geoengine Identify
    display_name = fields.Char(related="name", string="Order")
    street = fields.Char(related="location_id.street")
    street2 = fields.Char(related="location_id.street2")
    zip = fields.Char(related="location_id.zip")
    city = fields.Char(related="location_id.city", string="City")
    state_name = fields.Char(related="location_id.state_id.name",
                             string='State', ondelete='restrict')
    country_name = fields.Char(related="location_id.country_id.name",
                               string='Country', ondelete='restrict')
    phone = fields.Char(related="location_id.phone", string="Location Phone")
    mobile = fields.Char(related="location_id.mobile")

    stage_name = fields.Char(related="stage_id.name", string="Stage Name")
    # Field for Stage Color
    custom_color = fields.Char(related="stage_id.custom_color",
                               string='Stage Color')

    # Template
    template_id = fields.Many2one('fsm.template', string="Template")
    category_ids = fields.Many2many('fsm.category', string="Categories")

    # Equipment used for Maintenance and Repair Orders
    equipment_id = fields.Many2one('fsm.equipment', string='Equipment')

    # Equipment used for all other Service Orders
    equipment_ids = fields.Many2many('fsm.equipment', string='Equipments')
    type = fields.Selection([], string='Type')

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['fsm.stage'].search([('stage_type',
                                                   '=', 'order')])
        return stage_ids

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fsm.order') \
                or _('New')
        if vals.get('request_early', False) and not vals.get(
                'scheduled_date_start'):
            req_date = fields.Datetime.from_string(vals['request_early'])
            # Round scheduled date start
            req_date = req_date.replace(minute=0, second=0)
            vals.update({'scheduled_date_start': str(req_date),
                         'request_early': str(req_date)})
        self._calc_scheduled_dates(vals)
        return super(FSMOrder, self).create(vals)

    @api.multi
    def write(self, vals):
        self._calc_scheduled_dates(vals)
        res = super(FSMOrder, self).write(vals)
        for order in self:
            if 'customer_id' not in vals and order.customer_id is False:
                order.customer_id = order.location_id.customer_id.id
        return res

    def _calc_scheduled_dates(self, vals):
        """Calculate scheduled dates and duration"""
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
            if vals['scheduled_date_start']:
                date_to_with_delta = fields.Datetime.from_string(
                    vals.get('scheduled_date_start')) + \
                    timedelta(hours=self.scheduled_duration)
                vals['scheduled_date_end'] = str(date_to_with_delta)

    def action_confirm(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_confirmed').id})

    def action_request(self):
        if not self.person_ids:
            raise ValidationError(_("Cannot move to Requested " +
                                    "until 'Request Workers' is filled in"))
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_requested').id})

    def action_assign(self):
        if self.person_id:
            return self.write({'stage_id': self.env.ref(
                'fieldservice.fsm_stage_assigned').id})
        else:
            raise ValidationError(_("Cannot move to Assigned " +
                                    "until 'Assigned To' is filled in"))

    def action_schedule(self):
        if self.scheduled_date_start and self.person_id:
            return self.write({'stage_id': self.env.ref(
                'fieldservice.fsm_stage_scheduled').id})
        else:
            raise ValidationError(_("Cannot move to Scheduled " +
                                    "until both 'Assigned To' and " +
                                    "'Scheduled Start Date' are filled in"))

    def action_enroute(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_enroute').id})

    def action_start(self):
        if not self.date_start:
            raise ValidationError(_("Cannot move to Start " +
                                    "until 'Actual Start' is filled in"))
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_started').id})

    def action_complete(self):
        if not self.date_end:
            raise ValidationError(_("Cannot move to Complete " +
                                    "until 'Actual End' is filled in"))
        if not self.resolution:
            raise ValidationError(_("Cannot move to Complete " +
                                    "until 'Resolution' is filled in"))
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
        if (self.scheduled_duration and self.scheduled_date_start):
            date_to_with_delta = fields.Datetime.from_string(
                self.scheduled_date_start) + \
                timedelta(hours=self.scheduled_duration)
            self.scheduled_date_end = str(date_to_with_delta)

    def copy_notes(self):
        self.description = ""
        if self.type not in ['repair', 'maintenance']:
            for equipment_id in self.equipment_ids:
                if equipment_id:
                    if equipment_id.notes is not False:
                        if self.description is not False:
                            self.description = (self.description +
                                                equipment_id.notes + '\n ')
                        else:
                            self.description = (equipment_id.notes + '\n ')
        else:
            if self.equipment_id:
                if self.equipment_id.notes is not False:
                    if self.description is not False:
                        self.description = (self.description +
                                            self.equipment_id.notes + '\n ')
                    else:
                        self.description = (self.equipment_id.notes + '\n ')
        if self.location_id:
            s = self.location_id.direction
            if s is not False and s is not '<p><br></p>':
                s = s.replace('<p>', '')
                s = s.replace('<br>', '')
                s = s.replace('</p>', '\n')
                if self.location_directions is not False:
                    self.location_directions = (self.location_directions +
                                                '\n' + s + '\n')
                else:
                    self.location_directions = (s + '\n ')
        if self.template_id:
            self.todo = self.template_id.instructions

    @api.onchange('location_id')
    def onchange_location_id(self):
        if self.location_id:
            self.territory_id = self.location_id.territory_id or False
            self.branch_id = self.location_id.branch_id or False
            self.district_id = self.location_id.district_id or False
            self.region_id = self.location_id.region_id or False
            self.copy_notes()

    @api.onchange('equipment_ids')
    def onchange_equipment_ids(self):
        self.copy_notes()

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            self.category_ids = self.template_id.category_ids
            self.scheduled_duration = self.template_id.hours
            self.copy_notes()


class FSMTeam(models.Model):
    _inherit = 'fsm.team'

    order_ids = fields.One2many(
        'fsm.order', 'team_id', string='Orders',
        domain=[('stage_id.is_closed', '=', False)])
