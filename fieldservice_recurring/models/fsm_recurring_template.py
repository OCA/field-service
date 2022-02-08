# Copyright (C) 2019 Brian McMaster, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMRecurringTemplate(models.Model):
    _name = "fsm.recurring.template"
    _description = "Recurring Field Service Order Template"
    _inherit = "mail.thread"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    description = fields.Text()
    fsm_frequency_set_id = fields.Many2one("fsm.frequency.set", "Frequency Set")
    max_orders = fields.Integer(
        string="Maximum Orders", help="Maximium number of orders that will be created"
    )
    fsm_order_template_id = fields.Many2one(
        "fsm.template",
        string="Order Template",
        help="This is the order template that will be recurring",
    )
    company_id = fields.Many2one("res.company", "Company")
