# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FsmTemplate(models.Model):
    _inherit = "fsm.template"

    subcontract_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Subcontracting Service Product",
        domain=[("type", "=", "service"), ("purchase_method", "=", "receive")],
        help="Service product used on the Purchase Order line when an FSO "
        "of this type is subcontracted to an external worker. The "
        "product should have invoicing policy 'Based on Received "
        "Quantities' and supplierinfo configured for each vendor.",
    )
