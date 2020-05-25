# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    fsm_order_ids = fields.Many2many(
        'fsm.order', 'fsm_order_account_payment',
        'payment_id', 'fsm_order_id', string='FSM Orders',
        compute='_compute_fsm_order_ids',
        store=True, index=True, copy=False)
    fsm_order_count = fields.Integer(
        string='FSM Order Count',
        compute='_compute_fsm_order_count', readonly=True)

    @api.depends('fsm_order_ids')
    def _compute_fsm_order_count(self):
        for payment in self:
            payment.fsm_order_count = len(payment.fsm_order_ids)

    @api.multi
    def action_view_fsm_orders(self):
        action = self.env.ref(
            'fieldservice.action_fsm_operation_order').read()[0]
        if self.fsm_order_count > 1:
            action['domain'] = [('id', 'in', self.fsm_order_ids)]
        elif self.fsm_order_ids:
            action['views'] = \
                [(self.env.ref('fieldservice.fsm_order_form').id, 'form')]
            action['res_id'] = self.fsm_order_ids[0].id
        return action

    @api.depends('invoice_ids.fsm_order_ids')
    def _compute_fsm_order_ids(self):
        fsm_order_ids = []
        for invoice in self.invoice_ids:
            if invoice.fsm_order_ids:
                fsm_order_ids.extend(invoice.fsm_order_ids.ids)
        if fsm_order_ids:
            self.fsm_order_ids = [(6, 0, fsm_order_ids)]
