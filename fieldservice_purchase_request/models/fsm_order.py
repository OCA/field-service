# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    purchase_request_ids = fields.One2many(
        "purchase.request", "fsm_order_id", string="Purchase Requests"
    )
    purchase_request_count = fields.Integer(
        compute="_compute_purchase_request_count", string="# Purchase Requests"
    )

    @api.depends("purchase_request_ids")
    def _compute_purchase_request_count(self):
        for order in self:
            order.purchase_request_count = len(order.purchase_request_ids)

    def action_create_purchase_request(self):
        self.ensure_one()
        request = self.env["purchase.request"].create(
            {
                "fsm_order_id": self.id,
                "origin": self.name,
                "requested_by": self.env.user.id,
                "company_id": self.company_id.id,
            }
        )
        return {
            "type": "ir.actions.act_window",
            "name": _("Request Parts"),
            "res_model": "purchase.request",
            "res_id": request.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_view_purchase_requests(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Purchase Requests"),
            "res_model": "purchase.request",
            "domain": [("fsm_order_id", "=", self.id)],
            "view_mode": "list,form",
            "context": {
                "default_fsm_order_id": self.id,
                "default_origin": self.name,
            },
        }
