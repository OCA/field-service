# Copyright (C) 2018 - TODAY, Open Source Integrators
# Copyright 2019 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    fsm_order_ids = fields.Many2many(
        'fsm.order', 'fsm_order_account_invoice_rel',
        'invoice_id', 'fsm_order_id', string='FSM Orders')
    fsm_order_count = fields.Integer(
        string='FSM Order Count',
        compute='_compute_fsm_order_count', readonly=True)

    @api.depends('fsm_order_ids')
    def _compute_fsm_order_count(self):
        for invoice in self:
            invoice.fsm_order_count = len(invoice.fsm_order_ids)

    @api.multi
    def action_view_fsm_orders(self):
        action = self.env.ref(
            'fieldservice.action_fsm_dash_order').read()[0]
        action['domain'] = [('invoice_ids', 'in', self.id)]
        return action
