# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    invoice_ids = fields.Many2many(
        'account.invoice', 'fsm_order_account_invoice_rel',
        'fsm_order_id', 'invoice_id', string='Invoices/Bills')
    invoice_count = fields.Integer(
        string='Invoice Count',
        compute='_compute_account_invoice_count', readonly=True)

    @api.depends('invoice_ids')
    def _compute_account_invoice_count(self):
        for order in self:
            order.invoice_count = len(order.invoice_ids)

    @api.multi
    def action_view_invoices(self):
        action = self.env.ref(
            'account.action_account_invoice').read()[0]
        action['domain'] = [('fsm_order_ids', 'in', self.id)]
        return action
