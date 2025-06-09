# Copyright (C) 2025 APSL-Nagarro Bernat Obrador bobrador@apsl.net
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class FsmOrderSignatureWizard(models.TransientModel):
    _name = "fsm.order.signature.wizard"
    _description = "FSM Order Signature Wizard"

    fsm_order_id = fields.Many2one(
        "fsm.order",
        string="FSM Order",
        required=True,
        ondelete="cascade",
    )
    signature = fields.Binary(required=True)

    def action_confirm(self):
        """Confirm the signature and update the FSM order and the SO."""
        now = fields.Datetime.now()
        self.fsm_order_id.signature = self.signature
        self.fsm_order_id.signed_by = self.fsm_order_id.location_id.partner_id.name
        self.fsm_order_id.signed_on = now

        if self.fsm_order_id.sale_id:
            self.fsm_order_id.sale_id.signature = self.signature
            self.fsm_order_id.sale_id.signed_by = (
                self.fsm_order_id.location_id.partner_id.name
            )
            self.fsm_order_id.sale_id.signed_on = now

        return {"type": "ir.actions.act_window_close"}
