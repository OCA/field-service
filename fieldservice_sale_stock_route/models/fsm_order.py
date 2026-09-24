# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import _, fields, models
from odoo.tools import format_datetime


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    show_postpone_button = fields.Boolean(
        compute="_compute_postpone_button_visibility", store=False
    )

    def write(self, vals):
        has_start_date = "scheduled_date_start" in vals
        raw_start_date = vals.get("scheduled_date_start")

        res = super().write(vals)

        sync_fields = {
            "scheduled_date_start",
            "scheduled_date_end",
            "scheduled_duration",
        }
        if sync_fields.intersection(vals) and not self.env.context.get("skip_fsm_sync"):
            for record in self:
                sale = record.sale_id
                if not sale:
                    continue

                if has_start_date:
                    if raw_start_date:
                        new_start = fields.Datetime.to_datetime(raw_start_date)
                        old_start = sale.commitment_date
                        # Calendar day changed -> Re-evaluate schedule hierarchy hours
                        if not old_start or old_start.date() != new_start.date():
                            dt_start, dt_end = sale._apply_time_range_to_dates(
                                new_start
                            )
                        else:
                            # Same day edit -> Preserve dispatcher's manual hours
                            dt_start = new_start
                            dt_end = record.scheduled_date_end
                    else:
                        # Blank date on FSM Order -> Clear dates
                        dt_start, dt_end = False, False
                else:
                    dt_start = record.scheduled_date_start
                    dt_end = record.scheduled_date_end

                # Delegate cross-model synchronization to SaleOrder helper
                sale._sync_fsm_and_picking_dates(dt_start, dt_end)

        return res

    def _is_valid_fsm_order(self, fsm_order):
        return bool(fsm_order.sale_id and fsm_order.sale_id.fsm_location_id)

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
            current_date = fsm_order.scheduled_date_start or fields.Datetime.now()
            new_date = sale_order._get_next_route_day(
                from_date=current_date + timedelta(days=1)
            )

            # Triggers write(), which detects the day change and re-resolves hours
            fsm_order.write({"scheduled_date_start": new_date})

            date_str = format_datetime(self.env, fsm_order.scheduled_date_start)
            fsm_order.message_post(
                body=_("Delivery postponed. New scheduled date: %s.") % date_str,
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
            )
