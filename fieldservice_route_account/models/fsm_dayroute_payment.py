# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMRoutePayment(models.Model):
    _name = 'fsm.route.dayroute.payment'
    _rec_name = 'journal_id'
    _description = 'Field Service Dayroute Payment'

    journal_id = fields.Many2one('account.journal', string='Journal')
    amount_collected = fields.Float(
        string='Collected Amount', readonly=True,
        compute='_compute_amount_collected')
    amount_counted = fields.Float(
        string='Counted Amount',
        default=0.0)
    difference = fields.Float(
        string='Difference', compute='_compute_amount_difference')
    move_id = fields.Many2one('account.move',
                              string='Journal Entry',
                              readonly=True)
    dayroute_id = fields.Many2one('fsm.route.dayroute', string='Day Route')

    def _compute_amount_collected(self):
        """Returns total amount collected by worker"""
        account_payment_obj = self.env['account.payment']
        for dayroute_payment in self:
            amount = 0
            for fsm_order in dayroute_payment.dayroute_id.order_ids:
                payment_ids = account_payment_obj.search(
                    [('journal_id', '=', dayroute_payment.journal_id.id),
                     ('fsm_order_ids', 'in', [fsm_order.id])])
                for payment in payment_ids:
                    amount = amount + payment.amount
            dayroute_payment.amount_collected = amount

    @api.depends('amount_collected', 'amount_counted')
    def _compute_amount_difference(self):
        """Returns difference between amount collect and
        amount given to the manager"""
        for dayroute_payment in self:
            dayroute_payment.difference = dayroute_payment.amount_collected - \
                dayroute_payment.amount_counted
