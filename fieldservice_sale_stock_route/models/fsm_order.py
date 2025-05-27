# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import _, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    show_postpone_button = fields.Boolean(
        compute="_compute_postpone_button_visibility", store=False
    )

    def write(self, vals):
        res = super().write(vals)

        if vals.get("scheduled_date_start") or vals.get("scheduled_date_end"):
            for record in self:
                if record.sale_id:
                    sale = record.sale_id

                    old_start = sale.commitment_date
                    old_end = sale.commitment_date_end

                    new_start = record.scheduled_date_start
                    new_end = record.scheduled_date_end

                    changes = []

                    if old_start != new_start:
                        sale.commitment_date = new_start
                        changes.append(
                            _("- Delivery Date: %(old)s → %(new)s")
                            % {
                                "old": old_start or "—",
                                "new": new_start or "—",
                            }
                        )

                    if old_end != new_end:
                        sale.commitment_date_end = new_end
                        changes.append(
                            _("- Delivery End Date: %(old)s → %(new)s")
                            % {
                                "old": old_end or "—",
                                "new": new_end or "—",
                            }
                        )

                    if changes:
                        body = _("<b>Updated Delivery Dates:</b><br/>") + "<br/>".join(
                            changes
                        )
                        sale.message_post(
                            body=body, subtype_id=self.env.ref("mail.mt_note").id
                        )

        return res

    def _is_valid_fsm_order(self, fsm_order):
        required_fields = [
            fsm_order.sale_id,
            fsm_order.sale_id.fsm_location_id,
            fsm_order.sale_id.fsm_location_id.fsm_route_id,
            fsm_order.sale_id.fsm_location_id.fsm_route_id.fsm_person_id,
            fsm_order.sale_id.fsm_location_id.fsm_route_id.day_ids,
        ]
        return all(required_fields)

    def _compute_postpone_button_visibility(self):
        for fsm_order in self:
            fsm_order.show_postpone_button = self._is_valid_fsm_order(
                fsm_order
            ) and any(
                picking.state not in ["done", "cancel"]
                for picking in fsm_order.picking_ids
            )

    def action_postpone_delivery(self):
        for fsm_order in self.filtered(self._is_valid_fsm_order):
            sale_order = fsm_order.sale_id
            new_commitment_date = sale_order._get_next_route_day(
                from_date=sale_order.commitment_date + timedelta(days=1)
            )
            date_diff = (new_commitment_date - sale_order.commitment_date).days

            sale_order.write(
                {
                    "commitment_date": new_commitment_date,
                    "commitment_date_end": sale_order.commitment_date_end
                    + timedelta(days=date_diff),
                }
            )

            fsm_order.message_post(
                body=_("Delivery postponed. New scheduled date: %s.")
                % new_commitment_date.strftime("%d/%m/%Y"),
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
            )
