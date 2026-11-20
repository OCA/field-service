# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, fields, models


class FSMEquipment(models.Model):
    _inherit = "fsm.equipment"

    purchase_request_count = fields.Integer(
        compute="_compute_purchase_request_count", string="# Purchase Requests"
    )

    def _get_purchase_request_domain(self):
        return [("fsm_order_id.equipment_ids", "in", self.ids)]

    def _compute_purchase_request_count(self):
        PurchaseRequest = self.env["purchase.request"]
        for equipment in self:
            equipment.purchase_request_count = PurchaseRequest.search_count(
                equipment._get_purchase_request_domain()
            )

    def action_view_purchase_requests(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Purchase Requests"),
            "res_model": "purchase.request",
            "domain": self._get_purchase_request_domain(),
            "view_mode": "list,form",
            "context": {"create": False},
        }
