# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

import pytz

from odoo import _, http
from odoo.exceptions import ValidationError
from odoo.http import request

from odoo.addons.website_sale.controllers import main as website_sale_controller


class FieldServiceController(http.Controller):
    @http.route(
        "/fieldservice/get_calendar_config", type="json", website=True, auth="user"
    )
    def get_calendar_config(self):
        """Fetch the max date configuration values from the settings."""
        config = request.env["res.config.settings"].sudo().get_values()
        return {
            "max_date_number": config.get("max_date_number", "1"),
            "max_date_unit": config.get("max_date_unit", "months"),
        }

    @http.route(
        "/fieldservice/get_route_info", type="json", website=True, auth="public"
    )
    def get_route_info(self):
        """Fetch the route info to check if a route is assigned to the user."""

        sale_order = (
            request.env["sale.order"]
            .sudo()
            .browse(request.session.get("sale_order_id"))
        )

        # Ensure sale_order exists and has a shipping partner with FSM location
        route = sale_order.partner_shipping_id.fsm_location_id.fsm_route_id

        # Check if route exists and has the required attributes
        route_assigned = bool(route and route.day_ids and route.fsm_person_id)

        return {"route_assigned": route_assigned}

    @http.route(
        "/fieldservice/get_enabled_days", type="json", website=True, auth="public"
    )
    def get_enabled_days(self):
        """Fetch enabled days of the week based on FSM routes."""
        sale_order = (
            request.env["sale.order"].sudo().browse(request.session["sale_order_id"])
        )
        fsm_location = sale_order.partner_shipping_id.fsm_location_id
        fsm_route = fsm_location.fsm_route_id
        enabled_days = []

        if fsm_route:
            # Map FSM Odoo day IDs (1=Monday, ..., 7=Sunday)
            # to datepicker days (0=Sunday, ..., 6=Saturday)
            day_id_to_index = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 0}
            enabled_days = [
                day_id_to_index[day]
                for day in fsm_route.day_ids.mapped("id")
                if day in day_id_to_index
            ]

        sale_orders = (
            request.env["sale.order"]
            .sudo()
            .search(
                [
                    ("state", "in", ["sale", "done"]),
                    ("fsm_location_id", "=", fsm_location.id),
                    (
                        "commitment_date",
                        ">",
                        datetime.now(),
                    ),
                ]
            )
        )

        active_orders = sale_orders.filtered(
            lambda so: not so.fsm_order_ids
            or any(not fsm.is_closed for fsm in so.fsm_order_ids)
        )

        busy_dates = [
            order.commitment_date.date().strftime("%Y-%m-%d")
            for order in active_orders
            if order.commitment_date
        ]

        return {
            "enabled_days": enabled_days,
            "busy_dates": busy_dates,
            "route_assigned": fsm_route,
        }

    @http.route("/fieldservice/get_blackout_days", type="json", auth="public")
    def get_blackout_days(self):
        """Fetch all blackout days to disable them on the calendar."""
        blackout_days = request.env["fsm.blackout.day"].sudo().search([])
        return {
            "disabled_dates": [
                fd.date.strftime("%Y-%m-%d") for fd in blackout_days if fd.date
            ]
        }

    @http.route("/fieldservice/get_time_ranges", type="json", auth="user")
    def get_time_ranges(self):
        sale_order = (
            request.env["sale.order"].sudo().browse(request.session["sale_order_id"])
        )
        fsm_location = sale_order.partner_shipping_id.fsm_location_id
        fsm_route = fsm_location.fsm_route_id

        domain = []
        if fsm_route:
            domain = ["|", ("route_id", "=", fsm_route.id), ("route_id", "=", False)]
        else:
            domain = [("route_id", "=", False)]

        time_ranges = request.env["fsm.delivery.time.range"].sudo().search(domain)
        time_range_data = [{"id": tr.id, "name": tr.name} for tr in time_ranges]

        return {"time_ranges": time_range_data}


class PaymentPortal(website_sale_controller.PaymentPortal):
    @http.route()
    def shop_payment_transaction(self, *args, **kwargs):
        selected_date = kwargs.get("selected_date")
        selected_time_range = kwargs.get("selected_time_range")

        config = request.env["res.config.settings"].sudo().get_values()
        auto_assign = config.get("auto_assign_default_time_range", False)

        if not selected_date:
            raise ValidationError(_("Please select a delivery date."))

        if not selected_time_range and auto_assign:
            time_range_default_id = config.get("time_range_default_id")
            if time_range_default_id:
                time_range = (
                    request.env["fsm.delivery.time.range"]
                    .sudo()
                    .browse(time_range_default_id)
                )
                if time_range.exists():
                    selected_time_range = time_range.id
                    kwargs["selected_time_range"] = selected_time_range

        if not selected_time_range:
            raise ValidationError(_("Please select a delivery time range."))

        order = (
            request.env["sale.order"].sudo().search([("id", "=", kwargs["order_id"])])
        )
        time_range = (
            request.env["fsm.delivery.time.range"]
            .sudo()
            .search([("id", "=", selected_time_range)])
        )

        user_timezone = pytz.timezone(request.env.user.tz or "UTC")
        start_datetime_utc = self._calculate_datetime(
            selected_date, time_range.start_time, user_timezone
        )
        end_datetime_utc = self._calculate_datetime(
            selected_date, time_range.end_time, user_timezone
        )

        order.commitment_date = start_datetime_utc
        order.commitment_date_end = end_datetime_utc

        return super().shop_payment_transaction(*args, **kwargs)

    def _calculate_datetime(self, selected_date, time_value, timezone):
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d")
        localized_datetime = timezone.localize(
            selected_date
            + timedelta(
                hours=int(time_value),
                minutes=int((time_value % 1) * 60),
            )
        )
        return localized_datetime.astimezone(pytz.utc).replace(tzinfo=None)
