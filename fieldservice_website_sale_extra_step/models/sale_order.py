# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, models

from odoo.addons.base.models.ir_qweb_fields import nl2br


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super().action_confirm()

        for order in self:
            active_fsm_order = self.env["fsm.order"].search(
                [
                    ("sale_id", "=", order.id),
                    ("sale_line_id", "=", False),
                    ("is_closed", "=", False),
                ]
            )

            # Propagate e-commerce extra step reference to fsm order
            active_fsm_order.write({"description": order.client_order_ref})

            # Propagate e-commerce extra step feedback to fsm order
            customer_message = order.message_ids.filtered(
                lambda m: m.message_type == "comment" and not m.subtype_id,
            )

            if customer_message:
                customer_message = customer_message[0]
                values = {
                    "body": nl2br(customer_message.body),
                    "model": "fsm.order",
                    "message_type": "comment",
                    "res_id": active_fsm_order.id,
                }
                self.env["mail.message"].with_user(SUPERUSER_ID).create(values)

            # Propagate e-commerce extra step document to fsm order
            attachment = self.env["ir.attachment"].search(
                [
                    ("res_model", "=", "sale.order"),
                    ("res_id", "=", order.id),
                    ("website_id", "!=", False),
                    ("create_uid", "!=", 1),
                ],
                limit=1,
            )

            if attachment:
                attachment_data = {
                    "name": attachment.name,
                    "datas": attachment.datas,
                    "res_model": "fsm.order",
                    "res_id": active_fsm_order.id,
                    "mimetype": attachment.mimetype,
                }

                fsm_attachment = (
                    self.env["ir.attachment"].sudo().create(attachment_data)
                )

                values = {
                    "body": "<p>Attached file from client:</p>",
                    "model": "fsm.order",
                    "message_type": "comment",
                    "res_id": active_fsm_order.id,
                    "attachment_ids": [(6, 0, [fsm_attachment.id])],
                    "subtype_id": self.env.ref("mail.mt_comment").id,
                }
                self.env["mail.message"].with_user(SUPERUSER_ID).create(values)

        return res
