# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import uuid
from datetime import timedelta

import pytz
from markupsafe import Markup

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import format_datetime

from odoo.addons.resource.models.utils import Intervals

ICS_DT_FORMAT = "%Y%m%dT%H%M%SZ"


class FSMOrder(models.Model):
    _inherit = ["fsm.order", "portal.mixin"]
    _name = "fsm.order"

    appointment_state = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("requested", "Requested"),
            ("rescheduled", "Rescheduled"),
            ("confirmed", "Confirmed"),
        ],
        string="Appointment Status",
        default="pending",
        required=True,
        tracking=True,
        copy=False,
    )
    appointment_confirmed_date = fields.Datetime(
        string="Appointment Confirmed On",
        readonly=True,
        copy=False,
    )
    appointment_confirmed_by = fields.Char(
        readonly=True,
        copy=False,
    )
    appointment_reschedule_count = fields.Integer(
        string="Reschedule Count",
        default=0,
        readonly=True,
        copy=False,
    )
    can_request_confirmation = fields.Boolean(
        compute="_compute_can_request_confirmation",
    )
    appointment_calendar_label = fields.Char(
        string="Calendar Label",
        compute="_compute_appointment_calendar_label",
        inverse="_inverse_appointment_calendar_label",
        store=True,
        help="Order name shown in the calendar, prefixed with a mark when the "
        "appointment is confirmed.",
    )

    @api.depends("name", "appointment_state")
    def _compute_appointment_calendar_label(self):
        for order in self:
            prefix = "✅ " if order.appointment_state == "confirmed" else ""
            order.appointment_calendar_label = f"{prefix}{order.name or ''}"

    def _inverse_appointment_calendar_label(self):
        return

    appointment_state_label = fields.Char(
        string="Appointment Status Label",
        compute="_compute_appointment_state_label",
    )

    @api.depends("appointment_state", "appointment_reschedule_count")
    def _compute_appointment_state_label(self):
        labels = dict(self._fields["appointment_state"].selection)
        for order in self:
            label = labels.get(order.appointment_state, "")
            if order.appointment_state == "confirmed" and (
                order.appointment_reschedule_count
            ):
                label = _("Confirmed (rescheduled)")
            order.appointment_state_label = label

    @api.depends(
        "stage_id.allow_confirmation_request",
        "person_id",
        "scheduled_date_start",
        "location_id.partner_id.email",
        "appointment_state",
    )
    def _compute_can_request_confirmation(self):
        for order in self:
            partner = order.location_id.partner_id
            order.can_request_confirmation = bool(
                order.stage_id.allow_confirmation_request
                and order.person_id
                and order.scheduled_date_start
                and partner
                and partner.email
                and order.appointment_state != "confirmed"
            )

    def _compute_access_url(self):
        for order in self:
            order.access_url = f"/fieldservice/appointment/{order.id}/confirm"

    def _regenerate_appointment_token(self):
        """Force a brand new access token, invalidating any previous link."""
        for order in self:
            order.sudo().write({"access_token": str(uuid.uuid4())})

    def _get_appointment_url(self, action):
        """Absolute public URL for the given action ('confirm'/'reschedule')."""
        self.ensure_one()
        return (
            f"{self.get_base_url()}/fieldservice/appointment/"
            f"{self.id}/{action}?access_token={self.access_token or ''}"
        )

    def _check_appointment_access(self, access_token):
        """Return True when the token is valid and the order still accepts
        the customer action. Rejects closed stages (REQ-024)."""
        self.ensure_one()
        if not access_token or not self.access_token:
            return False
        if not self.sudo().access_token == access_token:
            return False
        if self.sudo().stage_id.is_closed:
            return False
        return True

    def _is_appointment_past(self):
        """True when the scheduled start is already in the past. A past
        appointment can no longer be confirmed online (only rescheduled)."""
        self.ensure_one()
        start = self.sudo().scheduled_date_start
        return bool(start and start < fields.Datetime.now())

    def action_request_appointment_confirmation(self):
        self.ensure_one()
        if not self.can_request_confirmation:
            raise UserError(
                _(
                    "This order does not meet the prerequisites to request an "
                    "appointment confirmation (enabled stage, assigned worker, "
                    "scheduled date and customer email)."
                )
            )
        self._regenerate_appointment_token()
        template = self.env.ref(
            "fieldservice_appointment_confirmation.mail_template_appointment_request",
            raise_if_not_found=False,
        )
        view = self.env.ref(
            "fieldservice_appointment_confirmation."
            "fsm_appointment_confirmation_wizard_form"
        )
        ctx = {
            "default_model": "fsm.order",
            "default_res_ids": self.ids,
            "default_composition_mode": "comment",
            "default_template_id": template.id if template else False,
            "force_email": True,
        }
        return {
            "type": "ir.actions.act_window",
            "name": _("Request Appointment Confirmation"),
            "res_model": "fsm.appointment.confirmation.wizard",
            "view_mode": "form",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "context": ctx,
        }

    def _mark_appointment_requested(self):
        """Called by the wizard once the email has actually been sent."""
        for order in self:
            if order.appointment_state != "confirmed":
                order.appointment_state = "requested"

    def confirm_appointment(self, confirmed_by=None):
        self.ensure_one()
        partner = self.location_id.partner_id
        self.write(
            {
                "appointment_state": "confirmed",
                "appointment_confirmed_date": fields.Datetime.now(),
                "appointment_confirmed_by": confirmed_by or (partner and partner.name),
            }
        )
        self.message_post(
            body=_(
                "The customer %(name)s confirmed the appointment scheduled for "
                "%(date)s."
            )
            % {
                "name": confirmed_by or (partner and partner.name) or "",
                "date": format_datetime(self.env, self.scheduled_date_start),
            },
            subtype_xmlid="mail.mt_comment",
            partner_ids=self.person_id.partner_id.ids,
        )
        self._notify_appointment_confirmed()
        return True

    def _notify_appointment_confirmed(self):
        template = self.env.ref(
            "fieldservice_appointment_confirmation."
            "mail_template_appointment_confirmed",
            raise_if_not_found=False,
        )
        if not template:
            return
        for order in self:
            body = template._render_field("body_html", order.ids)[order.id]
            order.message_post(body=body, subtype_xmlid="mail.mt_comment")

    def reschedule_appointment(self, new_start):
        self.ensure_one()
        if not self._is_slot_available(new_start):
            raise ValidationError(_("The selected time slot is no longer available."))
        old_start = self.scheduled_date_start
        duration = self.scheduled_duration or self._get_slot_duration_hours()
        partner = self.location_id.partner_id
        self.write(
            {
                "scheduled_date_start": new_start,
                "scheduled_date_end": new_start + timedelta(hours=duration),
                "appointment_state": "confirmed",
                "appointment_confirmed_date": fields.Datetime.now(),
                "appointment_confirmed_by": partner and partner.name,
                "appointment_reschedule_count": self.appointment_reschedule_count + 1,
            }
        )
        self.message_post(
            body=Markup(
                _(
                    "The customer rescheduled and confirmed the appointment.<br/>"
                    "Original date: %(old)s<br/>New date: %(new)s"
                )
            )
            % {
                "old": format_datetime(self.env, old_start) if old_start else "-",
                "new": format_datetime(self.env, new_start),
            },
            subtype_xmlid="mail.mt_comment",
            partner_ids=self.person_id.partner_id.ids,
        )
        self._notify_appointment_rescheduled()
        return True

    def _notify_appointment_rescheduled(self):
        """Email the customer to confirm the new date (Ref: customer feedback)."""
        template = self.env.ref(
            "fieldservice_appointment_confirmation."
            "mail_template_appointment_rescheduled",
            raise_if_not_found=False,
        )
        if not template:
            return
        for order in self:
            template.send_mail(order.id, force_send=False)

    def _get_slot_duration_hours(self):
        param = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "fieldservice_appointment_confirmation.slot_duration_hours", "1.0"
            )
        )
        try:
            value = float(param)
        except (TypeError, ValueError):
            value = 1.0
        return value or 1.0

    def _get_reschedule_window_days(self):
        param = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "fieldservice_appointment_confirmation.reschedule_window_days", "14"
            )
        )
        try:
            value = int(param)
        except (TypeError, ValueError):
            value = 14
        return value or 14

    def _get_appointment_tz(self):
        """Customer timezone with fallback to the company one (REQ decision)."""
        self.ensure_one()
        partner = self.location_id.partner_id
        tz_name = (partner and partner.tz) or self.env.company.partner_id.tz or "UTC"
        try:
            return pytz.timezone(tz_name)
        except pytz.UnknownTimeZoneError:
            return pytz.UTC

    def _get_worker_calendar(self):
        self.ensure_one()
        return self.person_id.calendar_id or self.env.company.resource_calendar_id

    def _get_worker_busy_intervals(self, date_from, date_to):
        """Intervals already taken by other non-cancelled orders of the worker."""
        self.ensure_one()
        tz = self._get_appointment_tz()
        orders = self.sudo().search(
            [
                ("id", "!=", self.id),
                ("person_id", "=", self.person_id.id),
                ("stage_id.is_closed", "=", False),
                ("scheduled_date_start", "!=", False),
                ("scheduled_date_end", "!=", False),
                ("scheduled_date_start", "<", date_to.replace(tzinfo=None)),
                ("scheduled_date_end", ">", date_from.replace(tzinfo=None)),
            ]
        )
        intervals = []
        for order in orders:
            start = pytz.UTC.localize(order.scheduled_date_start).astimezone(tz)
            stop = pytz.UTC.localize(order.scheduled_date_end).astimezone(tz)
            intervals.append((start, stop, order))
        return Intervals(intervals)

    def _get_worker_available_slots(self, date_from, date_to):
        """Return a list of naive-UTC datetimes the worker is available.

        Ref: REQ-009, REQ-010. Slots respect the worker working schedule
        (resource.calendar, with company fallback) minus the orders already
        booked, sliced by the configured granularity.
        """
        self.ensure_one()
        calendar = self._get_worker_calendar()
        if not calendar:
            return []
        tz = self._get_appointment_tz()
        start_dt = pytz.UTC.localize(date_from).astimezone(tz)
        end_dt = pytz.UTC.localize(date_to).astimezone(tz)
        work_intervals = calendar._work_intervals_batch(start_dt, end_dt, tz=tz)[False]
        free = work_intervals - self._get_worker_busy_intervals(date_from, date_to)

        slot_hours = self._get_slot_duration_hours()
        needed = self.scheduled_duration or slot_hours
        step = timedelta(hours=slot_hours)
        needed_delta = timedelta(hours=needed)
        now = pytz.UTC.localize(fields.Datetime.now()).astimezone(tz)

        slots = []
        for start, stop, _meta in free:
            cursor = start
            while cursor + needed_delta <= stop:
                if cursor >= now:
                    slots.append(cursor.astimezone(pytz.UTC).replace(tzinfo=None))
                cursor += step
        return slots

    def _is_slot_available(self, new_start):
        """True when the whole [new_start, new_start + duration] interval fits
        in a single free working interval of the assigned worker."""
        self.ensure_one()
        calendar = self._get_worker_calendar()
        if not calendar:
            return False
        duration = self.scheduled_duration or self._get_slot_duration_hours()
        new_end = new_start + timedelta(hours=duration)
        tz = self._get_appointment_tz()
        start_dt = pytz.UTC.localize(new_start).astimezone(tz)
        end_dt = pytz.UTC.localize(new_end).astimezone(tz)
        work = calendar._work_intervals_batch(start_dt, end_dt, tz=tz)[False]
        free = work - self._get_worker_busy_intervals(new_start, new_end)
        return any(start <= start_dt and stop >= end_dt for start, stop, _meta in free)

    @staticmethod
    def _ics_escape(value):
        if not value:
            return ""
        return (
            str(value)
            .replace("\\", "\\\\")
            .replace(";", "\\;")
            .replace(",", "\\,")
            .replace("\n", "\\n")
        )

    def _get_appointment_ics(self):
        """Build an RFC 5545 VCALENDAR string for this order."""
        self.ensure_one()
        partner = self.location_id.partner_id
        start = self.scheduled_date_start
        duration = self.scheduled_duration or self._get_slot_duration_hours()
        end = self.scheduled_date_end or (start + timedelta(hours=duration))
        now = fields.Datetime.now()
        company = self.env.company
        location = ", ".join(
            part
            for part in [
                self.street,
                self.street2,
                self.city,
                self.zip,
                self.country_name,
            ]
            if part
        )
        description = _("Assigned worker: %s") % (self.person_id.name or "")
        if company.partner_id.phone:
            description += _("\\nContact: %s") % company.partner_id.phone
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//OCA//fieldservice_appointment_confirmation//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            "BEGIN:VEVENT",
            f"UID:fsm-order-{self.id}@{self.get_base_url().split('//')[-1]}",
            f"DTSTAMP:{now.strftime(ICS_DT_FORMAT)}",
            f"DTSTART:{start.strftime(ICS_DT_FORMAT)}",
            f"DTEND:{end.strftime(ICS_DT_FORMAT)}",
            f"SUMMARY:{self._ics_escape(self.name)}",
            f"LOCATION:{self._ics_escape(location)}",
            f"DESCRIPTION:{self._ics_escape(description)}",
        ]
        if company.partner_id.email:
            lines.append(
                f"ORGANIZER;CN={self._ics_escape(company.name)}:"
                f"mailto:{company.partner_id.email}"
            )
        if partner and partner.email:
            lines.append(
                f"ATTENDEE;CN={self._ics_escape(partner.name)}:"
                f"mailto:{partner.email}"
            )
        lines += ["END:VEVENT", "END:VCALENDAR"]
        return "\r\n".join(lines)
