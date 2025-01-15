# Copyright (C) 2024 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    purchase_ids = fields.One2many("purchase.order", "fsm_order_id", store=True)
    purchase_order_count = fields.Integer(
        compute="_compute_purchase_order_count", readonly=True
    )

    def action_view_purchase_orders(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "view_mode": "list,form",
            "domain": [("fsm_order_id", "=", self.id)],
            "context": {"default_fsm_order_id": self.id},
            "name": _("Purchase orders for Trip %s") % self.name,
        }

    @api.depends("purchase_ids")
    def _compute_purchase_order_count(self):
        for order in self:
            order.purchase_order_count = len(order.purchase_ids)

    @api.model_create_multi
    def create(self, vals):
        order = super().create(vals)
        if len(order.purchase_ids) > 0:
            for purchase in order.purchase_ids:
                purchase.fsm_order_id = order
        return order
