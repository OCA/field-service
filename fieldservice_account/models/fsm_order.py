# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    invoice_ids = fields.Many2many(
        'account.move', 'fsm_order_account_invoice_rel',
        'fsm_order_id', 'move_id', string='Invoices/Bills')
    invoice_count = fields.Integer(
        string='Invoice Count',
        compute='_compute_account_invoice_count', readonly=True)

    @api.depends('invoice_ids')
    def _compute_account_invoice_count(self):
        for order in self:
            order.invoice_count = len(order.invoice_ids)

    def action_view_invoices(self):
        action = self.env.ref(
            'account.action_move_out_invoice_type').read()[0]
        if self.invoice_count > 1:
            action['domain'] = [('id', 'in', self.invoice_ids.ids)]
        elif self.invoice_ids:
            action['views'] = \
                [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = self.invoice_ids[0].id
        return action
