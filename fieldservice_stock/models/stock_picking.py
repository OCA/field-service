# Copyright (C) 2018 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # fsm_order_id related field removed:
    # In Odoo 19, procurement.group model was removed, so group_id.fsm_order_id
    # is no longer available. This needs refactoring to use a different relationship.
    # TODO: Implement fsm_order_id as a direct Many2one field instead of related field.
    fsm_order_id = fields.Many2one(
        "fsm.order", string="Field Service Order", copy=False
    )
