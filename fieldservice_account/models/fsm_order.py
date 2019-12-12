# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    invoice_line_id = fields.Many2one(
        comodel_name="account.invoice.line",
        readonly=True,
        copy=False,
    )

    invoice_id = fields.Many2one(
        related="invoice_line_id.invoice_id",
        readonly=True,
    )
    invoice_ids = fields.One2many('account.invoice',
                                  'fsm_order_id',
                                  'Invoices'
                                  )
