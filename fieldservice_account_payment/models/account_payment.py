# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    fsm_order_ids = fields.Many2many(
        'fsm.order', 'fsm_order_account_payment',
        'payment_id', 'fsm_order_id', string='FSM Orders')
    fsm_order_count = fields.Integer(
        string='FSM Order Count',
        compute='_compute_fsm_order_count', readonly=True)

    @api.depends('payment_ids')
    def _compute_fsm_order_count(self):
        for payment in self:
            payment.fsm_order_count = len(payment.fsm_order_ids)

    @api.multi
    def action_view_fsm_orders(self):
        action = self.env.ref(
            'fieldservice.action_fsm_dash_order').read()[0]
        action['domain'] = [('payment_ids', 'in', self.id)]
        return action

    @api.depends('invoice_ids.fsm_order_ids')
    def compute_fsm_order_ids(self):
        self.fsm_order_ids = self.invoice_ids.fsm_order_ids
