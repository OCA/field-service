# Copyright (C) 2018 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    fsm_order_id = fields.Many2one(
        "fsm.order",
        string="Field Service Order",
        compute="_compute_fsm_order_id",
        store=True,
        readonly=False,
    )

    @api.depends("move_ids", "move_ids.fsm_order_id")
    def _compute_fsm_order_id(self):
        for picking in self:
            fsm_orders = picking.move_ids.mapped("fsm_order_id")
            picking.fsm_order_id = fsm_orders[:1]
