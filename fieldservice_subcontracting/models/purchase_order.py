# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    fsm_order_id = fields.Many2one(
        comodel_name="fsm.order",
        string="Field Service Order",
        copy=False,
        index=True,
        ondelete="set null",
        help="The Field Service Order that generated this Purchase Order.",
    )
    fsm_order_count = fields.Integer(
        compute="_compute_fsm_order_count",
        string="FSO Count",
    )

    @api.depends("fsm_order_id")
    def _compute_fsm_order_count(self):
        for po in self:
            po.fsm_order_count = 1 if po.fsm_order_id else 0

    def action_view_fsm_order(self):
        """Smart button action to open the linked FSO."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "fsm.order",
            "res_id": self.fsm_order_id.id,
            "view_mode": "form",
            "target": "current",
        }
