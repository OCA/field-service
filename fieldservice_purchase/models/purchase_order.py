# Copyright (C) 2024 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    fsm_order_id = fields.Many2one("fsm.order")

    def action_view_order(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "fsm.order",
            "view_mode": "form",
            "res_id": self.fsm_order_id.id,
            "target": "current",
            "name": _("FSM Order: %s") % self.ofsm_rder_id.name,
        }
