# Copyright (C) 2026 Innovyou
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMTemplate(models.Model):
    _inherit = "fsm.template"

    outgoing_picking_type_id = fields.Many2one(
        "stock.picking.type",
        string="Outgoing Operation Type",
        domain="[('code', '=', 'outgoing')]",
        help="Operation type used by default on orders of this template to "
        "create the transfer that sends materials out to the field service "
        "location. When empty, the warehouse default is used.",
    )
    incoming_picking_type_id = fields.Many2one(
        "stock.picking.type",
        string="Incoming Operation Type",
        domain="[('code', '=', 'incoming')]",
        help="Operation type used by default on orders of this template to "
        "create the transfer that receives materials back from the field "
        "service location. When empty, the warehouse default is used.",
    )
