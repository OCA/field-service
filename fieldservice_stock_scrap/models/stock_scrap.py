# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    fsm_order_id = fields.Many2one(
        "fsm.order", string="Field Service Order", ondelete="cascade"
    )
