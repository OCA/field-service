# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    payment_ids = fields.One2many('account.payment', 'fsm_order_id',
                                  string='Payments')
    payment_count = fields.Integer(
        string='Payment Count',
        compute='_compute_account_payment_count', readonly=True)

    @api.depends('payment_ids')
    def _compute_account_payment_count(self):
        for order in self:
            order.payment_count = len(order.payment_ids)

    @api.multi
    def action_view_payments(self):
        action = self.env.ref(
            'account.action_account_payment').read()[0]
        action['domain'] = [('fsm_order_id', '=', self.id)]
        return action
