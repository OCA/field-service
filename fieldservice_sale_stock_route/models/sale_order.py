# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import calendar
from datetime import datetime, time, timedelta

import pytz

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    commitment_date_end = fields.Datetime(
        string="Delivery End Date",
        readonly=True,
        copy=False,
        help="Expected delivery end time calculated based on location/route schedule.",
    )

    def _apply_time_range_to_dates(self, target_date):
        """Standardize start and end hours on a target date using
        the active fsm.location delivery schedule hierarchy."""
        self.ensure_one()
        if not target_date or not self.fsm_location_id:
            return False, False

        date_val = fields.Date.to_date(target_date)
        start_time, end_time = self.fsm_location_id.get_delivery_time_ranges(date_val)

        sh, sm = divmod(int(start_time * 60), 60)
        eh, em = divmod(int(end_time * 60), 60)

        dt_start = datetime.combine(date_val, time(sh, sm))
        dt_end = datetime.combine(date_val, time(eh, em))

        tz_name = self.env.context.get("tz") or self.env.user.tz or "UTC"
        local_tz = pytz.timezone(tz_name)

        dt_start = local_tz.localize(dt_start).astimezone(pytz.utc).replace(tzinfo=None)
        dt_end = local_tz.localize(dt_end).astimezone(pytz.utc).replace(tzinfo=None)

        return dt_start, dt_end

    def _sync_fsm_and_picking_dates(self, dt_start, dt_end):
        """Centralized synchronization across Sale Order, FSM Order,
        and Stock Pickings."""
        self.ensure_one()
        res = super(SaleOrder, self.with_context(skip_fsm_sync=True)).write(
            {
                "commitment_date": dt_start,
                "commitment_date_end": dt_end,
            }
        )

        picking_date = (
            dt_start or self.expected_date or self.date_order or fields.Datetime.now()
        )
        self.picking_ids.filtered(
            lambda p: p.state not in ("done", "cancel")
        ).with_context(skip_fsm_sync=True).write({"scheduled_date": picking_date})

        fsm_orders = self.env["fsm.order"].search(
            [
                ("sale_id", "=", self.id),
                ("sale_line_id", "=", False),
                ("is_closed", "=", False),
            ]
        )
        fsm_vals = {
            "scheduled_date_start": dt_start,
            "scheduled_date_end": dt_end,
        }
        if not dt_start:
            fsm_vals["scheduled_duration"] = 0.0

        fsm_orders.with_context(skip_fsm_sync=True).write(fsm_vals)
        return res

    def _prepare_fsm_values(self, **kwargs):
        res = super()._prepare_fsm_values(**kwargs)
        target_dt = self.commitment_date or self._get_next_route_day(
            from_date=fields.Datetime.now() + timedelta(days=1)
        )
        dt_start, dt_end = self._apply_time_range_to_dates(target_dt)

        res.update(
            {
                "request_early": dt_start,
                "scheduled_date_start": dt_start,
                "scheduled_date_end": dt_end,
            }
        )
        return res

    def write(self, vals):
        has_commitment_date = "commitment_date" in vals
        raw_commitment_date = vals.get("commitment_date")

        res = super().write(vals)

        if has_commitment_date and not self.env.context.get("skip_fsm_sync"):
            for order in self:
                if raw_commitment_date:
                    new_dt = fields.Datetime.to_datetime(raw_commitment_date)
                    dt_start, dt_end = order._apply_time_range_to_dates(new_dt)
                else:
                    dt_start, dt_end = False, False

                order._sync_fsm_and_picking_dates(dt_start, dt_end)

        return res

    def _action_confirm(self):
        for order in self:
            if any(
                sol.product_id.field_service_tracking != "no"
                for sol in order.order_line.filtered(
                    lambda x: x.display_type not in ("line_section", "line_note")
                )
            ):
                target_dt = order.commitment_date or order._get_next_route_day(
                    from_date=fields.Datetime.now() + timedelta(days=1)
                )
                dt_start, dt_end = order._apply_time_range_to_dates(target_dt)

                if order.fsm_location_id and order.fsm_location_id.fsm_route_id:
                    fsm_route = order.fsm_location_id.fsm_route_id
                    if fsm_route.day_ids and not fsm_route.force_schedule:
                        allowed_day_names = fsm_route.day_ids.mapped("name")
                        day_name = calendar.day_name[dt_start.weekday()]

                        if day_name not in allowed_day_names:
                            raise ValidationError(
                                _(
                                    "The selected delivery date "
                                    "(%(day)s) is not allowed "
                                    "for route %(route)s based on "
                                    "its schedule settings. Please "
                                    "choose a valid day or enable Force Schedule."
                                )
                                % {"route": fsm_route.name, "day": day_name}
                            )

                order.commitment_date = dt_start
                order.commitment_date_end = dt_end

        return super()._action_confirm()

    def _get_next_route_day(self, from_date=None):
        """Calculate the next available delivery day based on allowed days."""
        self.ensure_one()
        base_date = from_date or self.commitment_date or fields.Datetime.now()

        if not self.fsm_location_id:
            return base_date

        allowed_days = self.fsm_location_id.get_allowed_route_days()
        if not allowed_days:
            return base_date

        allowed_day_names = allowed_days.mapped("name")

        for i in range(7):
            test_date = base_date + timedelta(days=i)
            day_name = calendar.day_name[test_date.weekday()]
            if day_name in allowed_day_names:
                return test_date

        return base_date
