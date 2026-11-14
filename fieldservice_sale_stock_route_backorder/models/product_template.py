# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    create_backorder_sale = fields.Boolean(
        string="Create Backorder Sale Order",
        default=False,
        help="If checked, undelivered quantities of this product will "
        "generate a new sale order.",
    )
