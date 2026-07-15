# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import timedelta

import pytz

from odoo import fields, http
from odoo.http import request


class FSMAppointmentController(http.Controller):
    def _get_order(self, order_id, access_token):
        """Return the order (sudo) if the token grants access, else False."""
        order = request.env["fsm.order"].sudo().browse(order_id).exists()
        if not order or not order._check_appointment_access(access_token):
            return False
        return order

    def _render_invalid(self):
        company = request.env.company
        return request.render(
            "fieldservice_appointment_confirmation.appointment_invalid",
            {"company": company},
        )

    @http.route(
        "/fieldservice/appointment/<int:order_id>/confirm",
        type="http",
        auth="public",
        methods=["GET"],
        website=True,
    )
    def appointment_confirm_page(self, order_id, access_token=None, **kw):
        order = self._get_order(order_id, access_token)
        if not order:
            return self._render_invalid()
        if order._is_appointment_past() and order.appointment_state != "confirmed":
            return request.redirect(order._get_appointment_url("reschedule"))
        return request.render(
            "fieldservice_appointment_confirmation.appointment_confirm_page",
            {"order": order, "access_token": access_token},
        )

    @http.route(
        "/fieldservice/appointment/<int:order_id>/confirm",
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
        csrf=False,
    )
    def appointment_confirm_submit(self, order_id, access_token=None, **post):
        order = self._get_order(order_id, access_token)
        if not order:
            return self._render_invalid()
        if order._is_appointment_past() and order.appointment_state != "confirmed":
            return request.redirect(order._get_appointment_url("reschedule"))
        if order.appointment_state != "confirmed":
            order.confirm_appointment(confirmed_by=post.get("confirmed_by") or None)
        return request.render(
            "fieldservice_appointment_confirmation.appointment_confirmed",
            {"order": order, "access_token": access_token},
        )

    @http.route(
        "/fieldservice/appointment/<int:order_id>/reschedule",
        type="http",
        auth="public",
        methods=["GET"],
        website=True,
    )
    def appointment_reschedule_page(self, order_id, access_token=None, **kw):
        order = self._get_order(order_id, access_token)
        if not order:
            return self._render_invalid()
        date_from = fields.Datetime.now()
        date_to = date_from + timedelta(days=order._get_reschedule_window_days())
        slots = order._get_worker_available_slots(date_from, date_to)
        tz = order._get_appointment_tz()
        slots_by_day = {}
        for slot in slots:
            local = pytz.UTC.localize(slot).astimezone(tz)
            slots_by_day.setdefault(local.strftime("%Y-%m-%d"), []).append(
                {
                    "value": slot.strftime("%Y-%m-%d %H:%M:%S"),
                    "label": local.strftime("%H:%M"),
                }
            )
        return request.render(
            "fieldservice_appointment_confirmation.appointment_reschedule_page",
            {
                "order": order,
                "access_token": access_token,
                "slots_by_day": slots_by_day,
                "tz_name": str(tz),
                "appointment_past": order._is_appointment_past(),
            },
        )

    @http.route(
        "/fieldservice/appointment/<int:order_id>/reschedule",
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
        csrf=False,
    )
    def appointment_reschedule_submit(self, order_id, access_token=None, **post):
        order = self._get_order(order_id, access_token)
        if not order:
            return self._render_invalid()
        slot = post.get("slot")
        if not slot:
            return request.redirect(order._get_appointment_url("reschedule"))
        new_start = fields.Datetime.to_datetime(slot)
        try:
            order.reschedule_appointment(new_start)
        except Exception:  # noqa: BLE001 - show a friendly page on any failure
            return request.render(
                "fieldservice_appointment_confirmation.appointment_reschedule_page",
                {
                    "order": order,
                    "access_token": access_token,
                    "slots_by_day": {},
                    "error": True,
                },
            )
        return request.render(
            "fieldservice_appointment_confirmation.appointment_rescheduled",
            {"order": order, "access_token": access_token},
        )

    @http.route(
        "/fieldservice/appointment/<int:order_id>/ics",
        type="http",
        auth="public",
        methods=["GET"],
        website=True,
    )
    def appointment_ics(self, order_id, access_token=None, **kw):
        order = self._get_order(order_id, access_token)
        if not order:
            return self._render_invalid()
        content = order._get_appointment_ics()
        filename = f"appointment-{order.name or order.id}.ics"
        return request.make_response(
            content,
            headers=[
                ("Content-Type", "text/calendar; charset=utf-8"),
                ("Content-Disposition", f"attachment; filename={filename}"),
            ],
        )
