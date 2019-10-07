# Copyright 2019 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    fsm_order_count = fields.Integer(
        string='FSM Order Count',
        compute='_compute_fsm_order_ids', readonly=True)

    @api.depends('invoice_line_ids.fsm_order_ids')
    def _compute_fsm_order_ids(self):
        for invoice in self:
            if invoice.type == 'out_invoice':
                orders = invoice.invoice_line_ids.mapped('fsm_order_ids')
                invoice.fsm_order_count = len(orders)
            else:
                invoice.fsm_order_count = 0

    @api.multi
    def action_view_fsm_orders(self):
        # fetch all orders:
        # linked to this account
        line_ids = self.invoice_line_ids.ids
        action = self.env.ref(
            'fieldservice.action_fsm_dash_order').read()[0]
        action['domain'] = [('invoice_line_id', 'in', line_ids)]
        return action
