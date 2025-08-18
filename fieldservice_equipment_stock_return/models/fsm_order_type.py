# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author: Italo Lopes <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FsmOrderType(models.Model):
    _inherit = "fsm.order.type"

    internal_type = fields.Selection(
        selection_add=[("return", "Return")],
    )
    picking_type_id = fields.Many2one(
        "stock.picking.type",
        domain=[("code", "=", "incoming")],
    )
