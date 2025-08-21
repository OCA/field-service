# Copyright (C) 2025 APSL-Nagarro Bernat Obrador bobrador@apsl.net
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class FsmOrder(models.Model):
    _inherit = "fsm.order"

    signature = fields.Binary()
    signed_by = fields.Char()
    signed_on = fields.Datetime()

    def action_open_signature_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "fsm.order.signature.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_fsm_order_id": self.id},
        }
