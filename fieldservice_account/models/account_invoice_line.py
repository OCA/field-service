# Copyright 2019 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    fsm_order_ids = fields.One2many(
        comodel_name='fsm.order',
        inverse_name='invoice_line_id',
        string='FSM Orders',
        readonly=True, copy=False,
    )
