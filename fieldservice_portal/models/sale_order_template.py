from odoo import fields, models

from .fsm_order_type import SERVICE_TYPES


class SaleOrderTemplate(models.Model):
    _inherit = "sale.order.template"

    name = fields.Char(translate=True)
    service_type = fields.Selection(
        SERVICE_TYPES,
        default="other",
        required=True,
        help="Stable field-service purpose used independently of the translated name.",
    )
