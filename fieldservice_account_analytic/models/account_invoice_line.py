# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.model
    def create(self, vals):
        order = self.env['fsm.order'].browse(vals.get('fsm_order_id'))
        if order:
            if order.location_id.analytic_account_id:
                vals['account_analytic_id'] = order.location_id.\
                    analytic_account_id.id
            else:
                raise ValidationError(_("No analytic account "
                                        "set on the order's Location."))
        return super(AccountInvoiceLine, self).create(vals)
