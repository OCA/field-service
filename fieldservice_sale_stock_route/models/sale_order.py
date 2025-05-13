# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    commitment_date_end = fields.Datetime(
        string="Delivery End Date",
        compute="_compute_commitment_date_end",
        inverse="_inverse_set_commitment_date_end",
        store=True,
        copy=False,
        states={"done": [("readonly", True)], "cancel": [("readonly", True)]},
        help="This is the delivery deadline date promised to the customer. "
        "If set, the delivery order will be scheduled based on "
        "this date rather than product lead times.",
    )

    @api.depends("commitment_date")
    def _compute_commitment_date_end(self):
        for order in self:
            order.commitment_date_end = (
                max(
                    order.commitment_date,
                    order.commitment_date_end or order.commitment_date,
                )
                if order.commitment_date
                else False
            )

    def _inverse_set_commitment_date_end(self):
        for order in self:
            order.commitment_date_end = (
                max(order.commitment_date, order.commitment_date_end)
                if order.commitment_date_end and order.commitment_date
                else False
            )

    def _prepare_fsm_values(self, **kwargs):
        res = super()._prepare_fsm_values(**kwargs)
        next_route_day = self._get_next_route_day()

        fsm_date_values = {
            "request_early": self.commitment_date or next_route_day,
            "scheduled_date_start": self.commitment_date or next_route_day,
            "scheduled_date_end": self.commitment_date_end or next_route_day,
        }
        res.update(fsm_date_values)
        return res

    def write(self, values):
        res = super().write(values)
        for order in self:
            commitment_date = order.commitment_date or order._get_next_route_day()

            picking_values = {
                "scheduled_date": commitment_date,
            }
            fsm_order_values = {
                "request_early": commitment_date,
                "scheduled_date_start": commitment_date,
                "scheduled_date_end": order.commitment_date_end or commitment_date,
            }

            order.picking_ids.filtered(
                lambda r: r.state not in ["done", "cancel"]
            ).write(picking_values)
            fsm_orders = self.env["fsm.order"].search(
                [
                    ("sale_id", "=", order.id),
                    ("sale_line_id", "=", False),
                    ("is_closed", "=", False),
                ]
            )
            fsm_orders.write(fsm_order_values)

        return res

    def _action_confirm(self):
        for order in self:
            if any(
                sol.product_id.field_service_tracking != "no"
                for sol in order.order_line.filtered(
                    lambda x: x.display_type not in ("line_section", "line_note")
                )
            ):
                fsm_route = (
                    order.fsm_location_id.fsm_route_id
                    if order.fsm_location_id
                    else None
                )

                # Validate FSM route requirements
                if not fsm_route:
                    raise ValidationError(_("FSM Location must have a route set."))
                if not fsm_route.fsm_person_id:
                    raise ValidationError(_("FSM Route must have a person set."))
                if not fsm_route.day_ids:
                    raise ValidationError(_("FSM Route must have days set."))

                # Get allowed FSM days (1=Monday, 7=Sunday)
                allowed_days = fsm_route.day_ids.mapped("id")

                order.commitment_date = (
                    order.commitment_date or order._get_next_route_day()
                )

                # Convert weekday() days (0-6) to FSM days (1-7)
                scheduled_day = order.commitment_date.weekday() + 1
                if (
                    scheduled_day not in allowed_days
                    and not order.fsm_location_id.fsm_route_id.force_schedule
                ):
                    raise ValidationError(
                        _(
                            "The selected delivery date (%(day)s) is "
                            "not available for route %(route)s. "
                            "Please choose a valid date based on the available schedule, "
                            "or enable 'Force Schedule' on the route to override "
                            "this restriction."
                        )
                        % {
                            "route": fsm_route.name,
                            "day": order.commitment_date.strftime("%A"),
                        }
                    )

        return super()._action_confirm()

    def _get_next_route_day(self, from_date=None):
        """Calculate the next available FSM route day based on a given date."""
        self.ensure_one()

        fsm_route = self.fsm_location_id.fsm_route_id if self.fsm_location_id else None
        if not fsm_route or not fsm_route.day_ids:
            return fields.Datetime.now()

        route_days = sorted(map(int, fsm_route.day_ids))
        base_date = from_date or self.commitment_date or fields.Datetime.now()
        base_day = base_date.weekday() + 1  # Convert (0-6) to FSM days (1-7)

        # Find the next available route day or wrap around to the next week
        days_until_next = next(
            (d - base_day for d in route_days if d >= base_day),
            7 - base_day + route_days[0],
        )

        return base_date + timedelta(days=days_until_next)
