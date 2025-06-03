# Copyright 2025 Bernat Obrador (APSL-Nagarro)<bobrador@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    payment_mode = fields.Char(
        compute="_compute_payment_mode",
        store=True,
    )

    @api.depends("sale_id.payment_mode_id")
    def _compute_payment_mode(self):
        for order in self:
            payment_mode = False
            if order.sale_id:
                if order.sale_id.transaction_ids:
                    transaction = order.sale_id.transaction_ids[:1]

                    if transaction:
                        payment_mode = transaction.acquirer_id.name
                else:
                    payment_mode = order.sale_id.payment_mode_id.name
            order.payment_mode = payment_mode
