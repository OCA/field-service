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
        stage_ids = self.env['fsm.stage'].\
            search([('stage_type', '=', 'order'),
                    ('is_default', '=', True),
                    ('company_id', 'in', (self.env.user.company_id.id,
                                          False))],
                   order='sequence asc', limit=1)
        if stage_ids:
            return stage_ids[0]
        else:
            raise ValidationError(_(
                "You must create an FSM order stage first."))

    def _default_team_id(self):
        team_ids = self.env['fsm.team'].\
            search([('company_id', 'in', (self.env.user.company_id.id,
                                          False))],
                   order='sequence asc', limit=1)
        if team_ids:
            return team_ids[0]
        else:
            raise ValidationError(_(
                "You must create an FSM team first."))

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
                              default=lambda self: self._default_team_id(),
                              index=True, required=True,
                              track_visibility='onchange')

    # Request
    name = fields.Char(string='Name', required=True, index=True, copy=False,
                       default=lambda self: _('New'))

    location_id = fields.Many2one('fsm.location', string='Location',
                                  index=True, required=True)
    location_directions = fields.Char(string='Location Directions')
    request_early = fields.Datetime(string='Earliest Request Date',
                                    default=datetime.now())
    color = fields.Integer('Color Index')
    company_id = fields.Many2one(
        'res.company', string='Company', required=True, index=True,
        default=lambda self: self.env.user.company_id,
        help="Company related to this order")

    def _compute_request_late(self, vals):
        if vals.get('priority') == '0':
            if vals.get('request_early'):
                vals['request_late'] = fields.Datetime.\
                    from_string(vals.get('request_early')) + timedelta(days=3)
            else:
                vals['request_late'] = datetime.now() + timedelta(days=3)
        elif vals.get('priority') == '1':
            vals['request_late'] = fields.Datetime.\
                from_string(vals.get('request_early')) + timedelta(days=2)
        elif vals.get('priority') == '2':
            vals['request_late'] = fields.Datetime.\
                from_string(vals.get('request_early')) + timedelta(days=1)
        elif vals.get('priority') == '3':
            vals['request_late'] = fields.Datetime.\
                from_string(vals.get('request_early')) + timedelta(hours=8)
        return vals

    request_late = fields.Datetime(string='Latest Request Date')
    description = fields.Text(string='Description')

    person_ids = fields.Many2many('fsm.person',
                                  string='Field Service Workers')

    @api.onchange('location_id')
    def _onchange_location_id_customer(self):
        if self.company_id.auto_populate_equipments_on_order:
            fsm_equipment_rec = self.env['fsm.equipment'].search([
                ('current_location_id', '=', self.location_id.id)])
            self.equipment_ids = [(6, 0, fsm_equipment_rec.ids)]

    # Planning
    person_id = fields.Many2one('fsm.person', string='Assigned To',
                                index=True)
    person_phone = fields.Char(related="person_id.phone",
                               string="Worker Phone")
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
    type = fields.Many2one('fsm.order.type', string="Type")

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['fsm.stage'].\
            search([('stage_type', '=', 'order'),
                    ('company_id', '=', self.env.user.company_id.id)])
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
        if not vals.get('request_late'):
            if vals.get('priority') == '0':
                if vals.get('request_early'):
                    vals['request_late'] = \
                        fields.Datetime.from_string(vals.get('request_early'))\
                        + timedelta(days=3)
                else:
                    vals['request_late'] = datetime.now() + timedelta(days=3)
            elif vals.get('priority') == '1':
                vals['request_late'] = fields.Datetime.\
                    from_string(vals.get('request_early')) + timedelta(days=2)
            elif vals.get('priority') == '2':
                vals['request_late'] = fields.Datetime.\
                    from_string(vals.get('request_early')) + timedelta(days=1)
            elif vals.get('priority') == '3':
                vals['request_late'] = fields.Datetime.\
                    from_string(vals.get('request_early')) + timedelta(hours=8)
        return super(FSMOrder, self).create(vals)

    @api.multi
    def write(self, vals):
        self._calc_scheduled_dates(vals)
        res = super(FSMOrder, self).write(vals)
        return res

    def can_unlink(self):
        """:return True if the order can be deleted, False otherwise"""
        return self.stage_id == self._default_stage_id()

    @api.multi
    def unlink(self):
        for order in self:
            if order.can_unlink():
                res = super(FSMOrder, order).unlink()
            else:
                raise ValidationError(_(
                    "You cannot delete this order."))
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
        if (self.scheduled_duration and self.scheduled_date_start):
            date_to_with_delta = fields.Datetime.from_string(
                self.scheduled_date_start) + \
                timedelta(hours=self.scheduled_duration)
            self.scheduled_date_end = str(date_to_with_delta)

    def copy_notes(self):
        self.description = ""
        if self.type and self.type.name not in ['repair', 'maintenance']:
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
            if s is not False and s != '<p><br></p>':
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
            self.type = self.template_id.type_id


class FSMTeam(models.Model):
    _inherit = 'fsm.team'

    order_ids = fields.One2many(
        'fsm.order', 'team_id', string='Orders',
        domain=[('stage_id.is_closed', '=', False)])
