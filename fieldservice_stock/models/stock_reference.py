from odoo import fields, models


class StockReference(models.Model):
    _inherit = "stock.reference"

    fsm_order_ids = fields.Many2many(
        "fsm.order",
        "stock_reference_fsm_order_rel",
        "reference_id",
        "fsm_order_id",
        string="Field Service Orders",
    )
