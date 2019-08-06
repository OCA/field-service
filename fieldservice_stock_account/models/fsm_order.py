# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _
from odoo.exceptions import ValidationError


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    def _prepare_inv_line_for_stock_request(self, stock_request,
                                            invoice=False):
        accounts = stock_request.product_id.product_tmpl_id.\
            get_product_accounts()
        account = accounts['income']
        vals = {
            'product_id': stock_request.product_id.id,
            'quantity': stock_request.qty_done,
            'name': stock_request.product_id.name,
            'price_unit': 0,
            'show_in_report': False,
            'account_id': account.id,
            'invoice_id': invoice.id
        }
        return vals

    def _create_inv_line_for_stock_requests(self, invoice=False):
        for stock_request in self.stock_request_ids:
            vals = self._prepare_inv_line_for_stock_request(
                stock_request, invoice)
            self.env['account.invoice.line'].create(vals)

    def account_create_invoice(self):
        invoice = super().account_create_invoice()
        if self.location_id.inventory_location_id.usage == 'customer':
            self._create_inv_line_for_stock_requests(invoice)
        return invoice

    def account_no_invoice(self):
        res = super().account_no_invoice()
        if self.location_id.inventory_location_id.usage == 'customer':
            jrnl = self.env['account.journal'].search([
                ('company_id', '=', self.env.user.company_id.id),
                ('type', '=', 'sale'),
                ('active', '=', True)],
                limit=1)
            if self.bill_to == 'contact':
                if not self.customer_id:
                    raise ValidationError(_("Contact empty"))
                fpos = self.customer_id.property_account_position_id
                vals = {
                    'partner_id': self.customer_id.id,
                    'type': 'out_invoice',
                    'journal_id': jrnl.id or False,
                    'fiscal_position_id': fpos.id or False,
                    'fsm_order_id': self.id
                }
                invoice = self.env['account.invoice'].sudo().create(vals)
            else:
                fpos = self.location_id.customer_id.\
                    property_account_position_id
                vals = {
                    'partner_id': self.location_id.customer_id.id,
                    'type': 'out_invoice',
                    'journal_id': jrnl.id or False,
                    'fiscal_position_id': fpos.id or False,
                    'fsm_order_id': self.id
                }
                invoice = self.env['account.invoice'].sudo().create(vals)
            self._prepare_inv_line_for_stock_requests(invoice)
            # Validate and paid invoice
            invoice.action_invoice_open()
        return res
