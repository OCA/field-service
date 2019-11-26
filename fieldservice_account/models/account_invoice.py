# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    fsm_order_id = fields.Many2one('fsm.order', string='FSM Order')


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    fsm_order_id = fields.Many2one('fsm.order', string='FSM Order')
