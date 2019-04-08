# Copyright (C) 2019 - TODAY, Brian McMaster, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMRecurringTemplate(models.Model):
    _name = 'fsm.recurring.template'
    _description = 'Recurring Field Service Order Template'
    _inherit = "mail.thread"

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)
    description = fields.Text(string='Description')
    frequency_interval = fields.Integer(
        string="Repeat Every", help="Repeat every (Days/Week/Month/Year)",
        default=1, track_visibility='onchange')
    frequency_type = fields.Selection(
        string='Frequency Type', required=True,
        selection=[('day', 'Days'),
                   ('week', 'Weeks'),
                   ('month', 'Months'),
                   ('year', 'Years')])
    # end_date = fields.Date(string='End Date',
    #                        help="Recurring orders will not be made after this date")
    # max_orders = fields.Integer(string='Maximum Orders',
    #                             help="Maximium number of orders that will be created")
    fsm_order_template_id = fields.Many2one(
        'fsm.template', string='Order Template',
        help="This is the order template that will be recurring")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.user.company_id)
