# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    payment_ids = fields.Many2many(
        'account.payment', 'fsm_order_account_payment',
        'fsm_order_id', 'payment_id', string='Payments')
    payment_count = fields.Integer(
        string='Payment Count',
        compute='_compute_account_payment_count', readonly=True)

    @api.depends('payment_ids')
    def _compute_account_payment_count(self):
        for order in self:
            order.payment_count = len(order.payment_ids)

    @api.multi
    def action_view_payments(self):
        action = self.env.ref('account.action_account_payments').read()[0]
        if self.payment_count > 1:
            action['domain'] = [('id', 'in', self.payment_ids)]
        elif self.payment_ids:
            action['views'] = \
                [(self.env.ref('account.view_account_payment_form').id,
                  'form')]
            action['res_id'] = self.payment_ids[0].id
        return action
