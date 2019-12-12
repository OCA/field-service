# Copyright (C) 2018 - TODAY, Open Source Integrators
# Copyright 2019 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    fsm_order_ids = fields.One2many(
        comodel_name='fsm.order',
        string='FSM Orders',
        compute='_compute_fsm_order_ids',
        readonly=True, copy=False)
    fsm_order_count = fields.Integer(
        string='FSM Order Count',
        compute='_compute_fsm_order_ids', readonly=True)
    fsm_order_id = fields.Many2one('fsm.order', 'FSM Order')

    @api.depends('invoice_line_ids.fsm_order_id')
    def _compute_fsm_order_ids(self):
        for invoice in self:
            orders = invoice.invoice_line_ids.mapped('fsm_order_id')
            invoice.fsm_order_ids = orders
            invoice.fsm_order_count = len(orders)

    @api.multi
    def action_view_fsm_orders(self):
        # fetch all orders:
        # linked to this account
        line_ids = self.invoice_line_ids.ids
        action = self.env.ref(
            'fieldservice.action_fsm_dash_order').read()[0]
        action['domain'] = [('invoice_line_id', 'in', line_ids)]
        return action
