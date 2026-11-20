# Copyright (C) 2022 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    fsm_vehicle_in = fields.Boolean(
        "Used to load a Field Service Vehicle",
        default=False,
        help="""Check this box for operation types that will be used
        to load inventory on FSM Vehicles.""",
    )

    fsm_vehicle_out = fields.Boolean(
        "Used to unload a Field Service Vehicle",
        default=False,
        help="""Check this box for operation types that will be used
        to unload inventory from FSM Vehicles.""",
    )
