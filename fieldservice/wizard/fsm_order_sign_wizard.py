# Copyright 2025 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo import fields, models


class FSMOrderSignWizard(models.TransientModel):
    _name = "fsm.order.sign.wizard"
    _description = "FSM Order Sign Wizard"

    order_id = fields.Many2one(
        comodel_name="fsm.order",
        string="Order",
        required=True,
        ondelete="cascade",
    )
    signed_by = fields.Char(required=True)
    signature = fields.Image(required=True, max_width=1024, max_height=1024)

    def default_get(self, fields):
        res = super().default_get(fields)
        res["order_id"] = self.env.context.get("active_id")
        return res

    def action_sign(self):
        self.ensure_one()
        self.order_id.ensure_one()
        self.order_id.write(
            {
                "signed_by": self.signed_by,
                "signed_on": fields.Datetime.now(),
                "signature": self.signature,
            }
        )
        # Notify if the signature has been updated
        self.order_id.message_post(
            body=self.env._("Order signed by %s", self.order_id.signed_by),
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            attachments=[("sign", base64.decodebytes(self.order_id.signature))],
        )
        return True
