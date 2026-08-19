from odoo import fields, models


SERVICE_TYPES = [
    ("survey", "Site Survey"),
    ("installation", "Installation"),
    ("maintenance", "Maintenance"),
    ("repair", "Repair"),
    ("other", "Other"),
]


class FSMOrderType(models.Model):
    _inherit = "fsm.order.type"

    service_type = fields.Selection(
        SERVICE_TYPES,
        default="other",
        required=True,
        help="Stable workflow purpose used independently of the translated name.",
    )
