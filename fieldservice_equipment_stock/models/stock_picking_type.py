# Copyright (C) 2020 Gray Matter Logic, Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    create_fsm_equipment = fields.Boolean(
        string="Create FSM Equipment",
        help="Products with the 'Creates a FSM Equipment' flag "
        "will automatically be converted to an FSM Equipment.",
    )
