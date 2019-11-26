# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange('product_id', 'quantity')
    def onchange_product_id(self):
        for line in self:
            if line.fsm_order_id:
                partner = line.fsm_order_id.person_id and\
                    line.fsm_order_id.person_id.partner_id or False
                if not partner:
                    raise ValidationError(
                        _("Please set the field service worker."))
                fpos = partner.property_account_position_id
                tmpl = line.product_id.product_tmpl_id
                if line.product_id:
                    accounts = tmpl.get_product_accounts()
                    supinfo = self.env['product.supplierinfo'].search(
                        [('name', '=', partner.id),
                         ('product_tmpl_id', '=', tmpl.id),
                         ('min_qty', '<=', line.quantity)],
                        order='min_qty DESC')
                    line.price_unit = \
                        supinfo and supinfo[0].price or tmpl.standard_price
                    line.account_id = accounts.get('expense', False)
                    line.invoice_line_tax_ids = fpos.\
                        map_tax(tmpl.supplier_taxes_id)
                    line.name = line.product_id.name
