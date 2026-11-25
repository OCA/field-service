from odoo import api, fields, models
from odoo.tools import html2plaintext


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    order_title = fields.Char(
        compute="_compute_order_title",
        store=True,
        readonly=True,
        help="First non-empty line of the service order description.",
    )

    @api.depends("description")
    def _compute_order_title(self):
        for order in self:
            text = html2plaintext(order.description or "")
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            order.order_title = lines[0] if lines else False
