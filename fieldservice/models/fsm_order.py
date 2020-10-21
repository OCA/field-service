# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from odoo import api, fields, models, _
from . import fsm_stage
from odoo.exceptions import ValidationError, UserError


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

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'stage_id' in init_values:
            if self.stage_id.id == self.env.\
                    ref('fieldservice.fsm_stage_completed').id:
                return 'fieldservice.mt_order_completed'
            if self.stage_id.id == self.env.\
                    ref('fieldservice.fsm_stage_cancelled').id:
                return 'fieldservice.mt_order_cancelled'
        return super()._track_subtype(init_values)

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

    internal_type = fields.Selection(string='Internal Type',
                                     related='type.internal_type')

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [('stage_type', '=', 'order')]
        if self.env.context.get('default_team_id'):
            search_domain = [
                '&', ('team_ids', 'in', self.env.context['default_team_id'])
            ] + search_domain
        return stages.search(search_domain, order=order)

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
        vals.update(
            {'scheduled_date_end': self._context.get(
                'default_scheduled_date_end') or False})
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

    is_button = fields.Boolean(default=False)

    @api.multi
    def write(self, vals):
        if vals.get('stage_id', False) and vals.get('is_button', False):
            vals['is_button'] = False
        else:
            stage_id = self.env['fsm.stage'].browse(vals.get('stage_id'))
            if stage_id == self.env.ref('fieldservice.fsm_stage_completed'):
                raise UserError(_('Cannot move to completed from Kanban'))
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
                return super(FSMOrder, order).unlink()
            else:
                raise ValidationError(_(
                    "You cannot delete this order."))

    def _calc_scheduled_dates(self, vals):
        """Calculate scheduled dates and duration"""

        if (vals.get('scheduled_duration')
            or vals.get('scheduled_date_start')
                or vals.get('scheduled_date_end')):

            if (vals.get('scheduled_date_start')
                    and vals.get('scheduled_date_end')):
                new_date_start = fields.Datetime.from_string(vals.get(
                    'scheduled_date_start', False))
                new_date_end = fields.Datetime.from_string(
                    vals.get('scheduled_date_end', False))
                hours = new_date_end.replace(
                    second=0) - new_date_start.replace(second=0)
                hrs = hours.total_seconds() / 3600
                vals['scheduled_duration'] = float(hrs)

            elif vals.get('scheduled_date_end'):
                hrs = vals.get('scheduled_duration',
                               False) or self.scheduled_duration or 0
                date_to_with_delta = fields.Datetime.from_string(
                    vals.get('scheduled_date_end', False)
                ) - timedelta(hours=hrs)
                vals['scheduled_date_start'] = str(date_to_with_delta)

            elif (vals.get('scheduled_duration', False)
                  or (vals.get('scheduled_date_start', False)
                      and (self.scheduled_date_start != vals.get(
                          'scheduled_date_start', False)))):
                hours = vals.get('scheduled_duration', False)
                start_date_val = vals.get('scheduled_date_start',
                                          self.scheduled_date_start)
                start_date = fields.Datetime.from_string(start_date_val)
                date_to_with_delta = start_date + timedelta(hours=hours)
                vals['scheduled_date_end'] = str(date_to_with_delta)

    def action_complete(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_completed').id, 'is_button': True})

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
        old_desc = self.description
        self.description = ""
        self.location_directions = ""
        if self.type and self.type.name not in ['repair', 'maintenance']:
            for equipment_id in self.equipment_ids:
                if equipment_id:
                    if equipment_id.notes:
                        if self.description:
                            self.description = (self.description +
                                                equipment_id.notes + '\n ')
                        else:
                            self.description = (equipment_id.notes + '\n ')
        else:
            if self.equipment_id:
                if self.equipment_id.notes:
                    if self.description:
                        self.description = (self.description +
                                            self.equipment_id.notes + '\n ')
                    else:
                        self.description = (self.equipment_id.notes + '\n ')
        if self.location_id:
            self.location_directions = self.\
                _get_location_directions(self.location_id)
        if self.template_id:
            self.todo = self.template_id.instructions
        if self.description:
            self.description += '\n' + old_desc
        else:
            self.description = old_desc

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
            if self.template_id.type_id:
                self.type = self.template_id.type_id
            if self.template_id.team_id:
                self.team_id = self.template_id.team_id

    def _get_location_directions(self, location_id):
        self.location_directions = ""
        s = self.location_id.direction or ""
        parent_location = self.location_id.fsm_parent_id
        # ps => Parent Location Directions
        # s => String to Return
        while parent_location.id is not False:
            ps = parent_location.direction
            if ps:
                s += parent_location.direction
            parent_location = parent_location.fsm_parent_id
        return s

    @api.constrains('scheduled_date_start')
    def check_day(self):
        for rec in self:
            if rec.scheduled_date_start:
                holidays = self.env['resource.calendar.leaves'].search([
                    ('date_from', '>=', rec.scheduled_date_start),
                    ('date_to', '<=', rec.scheduled_date_start),
                ])
                if holidays:
                    raise ValidationError(_(
                        "%s is a holiday (%s)." %
                        (rec.scheduled_date_start.date(), holidays[0].name)
                    ))
