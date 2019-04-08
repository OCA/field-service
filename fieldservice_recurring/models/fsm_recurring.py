# Copyright (C) 2019 - TODAY, Brian McMaster, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class FSMRecurringOrder(models.Model):
    _name = 'fsm.recurring'
    _description = 'Recurring Field Service Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, index=True, copy=False,
                       default=lambda self: _('New'))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'In Progress'),
        ('pending', 'To Renew'),
        ('close', 'Closed'),
        ('cancel', 'Cancelled')], readonly=True,
        default='draft', track_visibility='onchange')
    fsm_recurring_template_id = fields.Many2one(
        'fsm.recurring.template', 'Recurring Template',
        required=True, readonly=True, 
        states={'draft': [('readonly', False)]})
    customer_id = fields.Many2one(
        'res.partner', string='Contact',
        domain=[('customer', '=', True)],
        change_default=True, index=True,
        track_visibility='always',)
    location_id = fields.Many2one(
        'fsm.location', string='Location', index=True, required=True)
    description = fields.Text(string='Description')
    frequency_interval = fields.Integer(
        string="Repeat Every", help="Repeat every (Days/Week/Month/Year)",
        default=1, track_visibility='onchange')
    frequency_type = fields.Selection(
        string='Frequency Type', required=True,
        selection=[('day', 'Day(s)'),
                   ('week', 'Week(s)'),
                   ('month', 'Month(s)'),
                   ('year', 'Year(s)')], default='day')
    start_date = fields.Datetime(String='Start Date')
    end_date = fields.Datetime(string='End Date',
                               help="Recurring orders will not be made after this date")
    # max_orders = fields.Integer(string='Maximum Orders',
    #                             help="Maximium number of orders that will be created")
    fsm_order_template_id = fields.Many2one(
        'fsm.template', string='Order Template', 
        help="This is the order template that will be recurring")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.user.company_id)
    fsm_order_ids = fields.One2many('fsm.order', 'fsm_recurring_id', string='Orders', 
                                    copy=False, readonly=True)
    fsm_order_count = fields.Integer('Orders Count', compute='_compute_order_count')
    next_request_date = fields.Datetime(string='Next Order Request Date', store=True,
                                        compute='_compute_next_request')

    _sql_constraints = [
        ('positive_frequency', 'CHECK(frequency_interval>=0)',
         'Frequency Interval must be positive')
    ]

    @api.multi
    @api.depends('fsm_order_ids')
    def _compute_order_count(self):
        data = self.env['fsm.order'].read_group(
            [('fsm_recurring_id', 'in', self.ids),
             ('stage_id', '!=', self.env.ref(
                 'fieldservice.fsm_stage_cancelled').id)],
            ['fsm_recurring_id'], ['fsm_recurring_id'])
        count_data = dict((item['fsm_recurring_id'][0],
                           item['fsm_recurring_id_count']) for item in data)
        for recurring in self:
            recurring.fsm_order_count = count_data.get(recurring.id, 0)

    @api.multi
    @api.depends('state', 'fsm_order_ids', 'frequency_interval', 'frequency_type')
    def _compute_next_request(self):
        for rec in self:
            if rec.state != 'progress':
                rec.next_request_date = False
            else:
                next_date = datetime.now()
                interval = rec.frequency_interval
                deltas = {
                    'year': relativedelta(years=+interval),
                    'month': relativedelta(months=+interval),
                    'week': relativedelta(weeks=+interval),
                    'day': relativedelta(days=+interval)
                }
                last_order = self.env['fsm.order'].search([
                    ('fsm_recurring_id', '=', rec.id),
                    ('stage_id', '!=', self.env.ref(
                        'fieldservice.fsm_stage_cancelled').id
                    )], offset=0, limit=1, order='request_early desc')
                if last_order:
                    last_date = fields.Datetime.from_string(last_order.request_early)
                    next_date = last_date + deltas.get(rec.frequency_type)
                rec.next_request_date = next_date

    @api.onchange('fsm_recurring_template_id')
    def onchange_recurring_template_id(self):
        if not self.fsm_recurring_template_id:
            return
        values = self.populate_from_template()
        self.update(values)

    def populate_from_template(self,template=False):
        if not template:
            template = self.fsm_recurring_template_id
        vals = {
            'frequency_interval': template.frequency_interval,
            'frequency_type': template.frequency_type,
            'description': template.description,
            'fsm_order_template_id': template.fsm_order_template_id,
            'company_id': template.company_id,
        }
        return vals

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fsm.recurring') \
                or _('New')
        return super(FSMRecurringOrder, self).create(vals)

    @api.multi
    def action_start(self):
        for rec in self:
            if rec.start_date == False:
                rec.start_date = datetime.now() 
            rec._create_next_order()
            rec.write({'state': 'progress'})

    @api.multi
    def action_renew(self):
        return self.action_start()

    @api.multi
    def action_cancel(self):
        for order in self.fsm_order_ids.filtered(
            lambda o: o.stage_id.is_closed == False
        ):
            order.action_cancel()
        return self.write({'state': 'cancel'})

    def _prepare_order_values(self):
        return {
            'fsm_recurring_id': self.id,
            'customer_id': self.customer_id.id,
            'location_id': self.location_id.id,
            'request_early': self.next_request_date or self.start_date,
            'description': self.description,
            'template_id': self.fsm_order_template_id.id,
            'company_id': self.company_id.id,
        }

    def _create_next_order(self):
        self.ensure_one()
        vals = self._prepare_order_values()
        return self.env['fsm.order'].create(vals)

    @api.model
    def _cron_generate_orders(self, days_ahead=30):
        """
        Executed by Cron task to create all of the orders 
            able to be requested within the next number of days ahead.
        @param {integer} days_ahead: an integer value used to set how many
           days in advance to create field service orders
        @return {recordset} orders: all the objects created within given days ahead
        """
        orders = self.env['fsm.order']
        request_thru_date = datetime.now() + relativedelta(days=+days_ahead)
        request_thru_str = request_thru_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        for recurring in self.env['fsm.recurring'].search([
            ('state', 'in', ('progress', 'renew')),
            ('next_request_date', '<=', request_thru_str)
        ]):
            if recurring.end_date and (recurring.end_date < request_thru_str):
                last_date = fields.Datetime.from_string(recurring.end_date)
            else:
                last_date = request_thru_date
            next_request = fields.Datetime.from_string(recurring.next_request_date)
            while next_request <= last_date:
                orders += recurring._create_next_order()
                next_request = fields.Datetime.from_string(recurring.next_request_date)
        return orders

    # @api.model
    # def _cron_manage_expiration(self):
    #     """
    #     Executed by Cron task 
    #     """
