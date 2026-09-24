# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    fsm_order_id = fields.Many2one(
        "fsm.order",
        string="Field Service Order",
        index=True,
        ondelete="set null",
        help="Field service order that originated this purchase request.",
    )
