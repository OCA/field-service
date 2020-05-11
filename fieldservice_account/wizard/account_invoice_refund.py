# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class AccountInvoiceRefund(models.TransientModel):
    _inherit = 'account.invoice.refund'

    @api.multi
    def compute_refund(self, mode='refund'):
        res = super().compute_refund(mode)
        inv_obj = self.env['account.invoice']
        context = dict(self._context or {})
        for invoice in inv_obj.browse(context.get('active_ids')):
            if len(invoice.fsm_order_ids) > 0:
                refunds = inv_obj.search([
                    ('refund_invoice_id', '=', invoice.id)])
                for refund in refunds:
                    refund.fsm_order_ids = [(6, 0, invoice.fsm_order_ids.ids)]
                if mode == 'modify':
                    new_inv = inv_obj.browse(res['res_id'])
                    new_inv.fsm_order_ids = [(6, 0, invoice.fsm_order_ids.ids)]
        return res
