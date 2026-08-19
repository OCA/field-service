import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import format_amount

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    portal_dayroute_id = fields.Many2one(
        "fsm.route.dayroute",
        string="Portal Appointment",
        copy=False,
        help="Appointment selected in the customer portal before payment.",
    )
    portal_service_description = fields.Text(
        string="Portal Service Description",
        copy=False,
    )

    def write(self, vals):
        result = super().write(vals)
        if "state" in vals:
            for order in self:
                try:
                    order._on_state_change(vals["state"])
                except Exception:
                    _logger.exception(
                        "Customer notification failed for sale.order %s", order.id
                    )
        return result

    def _get_service_type(self):
        self.ensure_one()
        return self.sale_order_template_id.service_type or "other"

    def _is_visit_released(self):
        self.ensure_one()
        if self._get_service_type() != "survey" or self.state != "sale":
            return False
        if self.company_id.visit_confirmation_policy == "payment":
            return self._is_paid()
        return True

    def _is_installation_released(self):
        self.ensure_one()
        if self._get_service_type() != "installation" or self.state != "sale":
            return False
        return (
            self.company_id.installation_release_policy == "approval"
            or self._is_paid()
        )

    def _has_to_be_signed(self):
        self.ensure_one()
        if (
            self._get_service_type() == "survey"
            and self.company_id.visit_confirmation_policy == "phone"
        ):
            return False
        return super()._has_to_be_signed()

    def _has_to_be_paid(self):
        self.ensure_one()
        if self._get_service_type() == "survey":
            if self.company_id.visit_confirmation_policy == "phone":
                return False
            return (
                self.state in ("draft", "sent")
                and not self.is_expired
                and self.amount_total > 0
                and not self._is_confirmation_amount_reached()
            )
        return super()._has_to_be_paid()

    def _get_prepayment_required_amount(self):
        self.ensure_one()
        if (
            self._get_service_type() == "survey"
            and self.company_id.visit_confirmation_policy == "payment"
        ):
            return self.currency_id.round(self.amount_total)
        return super()._get_prepayment_required_amount()

    def _is_confirmation_amount_reached(self):
        self.ensure_one()
        if (
            self._get_service_type() == "survey"
            and self.company_id.visit_confirmation_policy == "phone"
        ):
            return False
        return super()._is_confirmation_amount_reached()

    def _confirmation_error_message(self):
        self.ensure_one()
        error = super()._confirmation_error_message()
        if error:
            return error
        service_type = self._get_service_type()
        payment_required = (
            service_type == "survey"
            and self.company_id.visit_confirmation_policy == "payment"
        ) or (
            service_type == "installation"
            and self.company_id.installation_release_policy == "payment"
        )
        if payment_required and not self._is_paid():
            return _("This quotation must be fully paid before confirmation.")
        return False

    @api.model
    def _portal_dayroute_reservation_domain(self, dayroute, exclude_order=None):
        domain = [
            ("portal_dayroute_id", "=", dayroute.id),
            ("state", "in", ("draft", "sent")),
            "|",
            ("validity_date", "=", False),
            ("validity_date", ">=", fields.Date.context_today(self)),
        ]
        if exclude_order:
            domain.append(("id", "not in", exclude_order.ids))
        return domain

    @api.model
    def _portal_dayroute_reserved_capacity(self, dayroute, exclude_order=None):
        return self.sudo().search_count(
            self._portal_dayroute_reservation_domain(dayroute, exclude_order)
        )

    @api.model
    def _portal_dayroute_available_capacity(self, dayroute, exclude_order=None):
        return dayroute.order_remaining - self._portal_dayroute_reserved_capacity(
            dayroute, exclude_order
        )

    def _validate_portal_dayroute(
        self, service_type=None, needed_capacity=1, lock=False
    ):
        self.ensure_one()
        dayroute = self.portal_dayroute_id.exists()
        if not dayroute:
            raise ValidationError(_("Select an appointment."))
        if lock:
            dayroute.lock_for_update()
            dayroute.invalidate_recordset(
                ["date", "order_remaining", "route_id", "team_id"]
            )

        route_type = {
            "survey": "visit",
            "maintenance": "maintenance",
            "installation": "installation",
        }.get(service_type or self._get_service_type())
        if not route_type or dayroute.route_id.route_type != route_type:
            raise ValidationError(
                _("The selected appointment does not match this service.")
            )
        if dayroute.date < fields.Date.context_today(self):
            raise ValidationError(_("The selected appointment is no longer available."))
        if dayroute.team_id.company_id != self.company_id:
            raise ValidationError(
                _("The selected appointment is not available for this company.")
            )
        available_capacity = self._portal_dayroute_available_capacity(
            dayroute, exclude_order=self
        )
        if needed_capacity > available_capacity:
            raise ValidationError(
                _("The selected appointment has no remaining capacity.")
            )
        return dayroute

    def _portal_pending_fsm_count(self):
        self.ensure_one()
        pending_lines = self.order_line.filtered(
            lambda line: line.display_type not in ("line_section", "line_note")
            and line.product_id.field_service_tracking != "no"
            and not line.fsm_order_id
        )
        return len(
            pending_lines.filtered(
                lambda line: line.product_id.field_service_tracking == "line"
            )
        ) + bool(
            pending_lines.filtered(
                lambda line: line.product_id.field_service_tracking == "sale"
            )
        )

    def _prepare_fsm_values(self, **kwargs):
        values = super()._prepare_fsm_values(**kwargs)
        if self.portal_dayroute_id:
            dayroute = self.portal_dayroute_id
            values.update(
                {
                    "dayroute_id": dayroute.id,
                    "person_id": dayroute.person_id.id,
                    "team_id": dayroute.team_id.id,
                    "request_early": dayroute.date_start_planned,
                    "scheduled_date_start": dayroute.date_start_planned,
                }
            )
        if self.portal_service_description:
            values["description"] = self.portal_service_description
        return values

    def _field_service_generation(self):
        for order in self.filtered(
            lambda candidate: candidate._get_service_type() == "survey"
        ):
            if not order._is_visit_released():
                raise ValidationError(
                    _(
                        "The site survey must be confirmed according to the company "
                        "policy before scheduling."
                    )
                )
        for order in self.filtered("portal_dayroute_id"):
            pending_count = order._portal_pending_fsm_count()
            if pending_count:
                order._validate_portal_dayroute(
                    needed_capacity=pending_count,
                    lock=True,
                )
        return super()._field_service_generation()

    def _on_state_change(self, new_state):
        self.ensure_one()
        if not self.partner_id:
            return

        notifier = self.env["fieldservice.notification"].with_company(self.company_id)
        service_type = self._get_service_type()
        if new_state == "sent" and service_type == "installation":
            self._notify_installation_quote(self.partner_id, notifier)
        elif (
            new_state == "sale"
            and service_type == "survey"
            and self._is_visit_released()
        ):
            self._notify_survey_confirmed(self.partner_id, notifier)
        elif new_state == "sale" and service_type in ("maintenance", "repair"):
            self._notify_service_paid(self.partner_id, notifier)
        elif (
            new_state == "sale"
            and service_type == "installation"
            and self._is_installation_released()
        ):
            self._notify_installation_released(self.partner_id, notifier)

    def _is_installation_order(self):
        return self._get_service_type() == "installation"

    def _formatted_amount(self, amount):
        return format_amount(self.env, amount, self.currency_id)

    def _notify_installation_quote(self, partner, notifier):
        lines_text = "\n".join(
            self.env._(
                "%(product)s - %(amount)s",
                product=line.product_id.name or "",
                amount=self._formatted_amount(line.price_unit),
            )
            for line in self.order_line[:5]
        )
        portal_url = f"{notifier._get_base_url()}/my/orders/{self.id}"
        message = self.env._(
            "Your installation quotation is ready.\n%(lines)s\nTotal: %(total)s\n%(url)s",
            lines=lines_text,
            total=self._formatted_amount(self.amount_total),
            url=portal_url,
        )
        notifier.notify_customer(
            partner,
            message,
            email_template_xmlid="fieldservice_portal.email_installation_quote",
            email_values={"portal_url": portal_url},
        )

    def _notify_installation_paid(self, partner, notifier):
        portal_url = f"{notifier._get_base_url()}/my/installation/{self.id}"
        slots = notifier._get_available_slots_text("installation", limit=5)
        message = self.env._(
            "Payment received (%(amount)s). Choose an installation appointment: %(url)s",
            amount=self._formatted_amount(self.amount_total),
            url=portal_url,
        )
        if slots:
            message += self.env._("\n\nAvailable appointments:\n%(slots)s", slots=slots)
        notifier.notify_customer(
            partner,
            message,
            email_template_xmlid="fieldservice_portal.email_installation_paid",
            email_values={"portal_url": portal_url},
        )

    def _notify_installation_released(self, partner, notifier):
        if self.company_id.installation_release_policy == "payment":
            return self._notify_installation_paid(partner, notifier)

        portal_url = f"{notifier._get_base_url()}/my/installation/{self.id}"
        slots = notifier._get_available_slots_text("installation", limit=5)
        message = self.env._(
            "Your installation quotation has been approved. Choose an installation "
            "appointment: %(url)s",
            url=portal_url,
        )
        if slots:
            message += self.env._("\n\nAvailable appointments:\n%(slots)s", slots=slots)
        notifier.notify_customer(
            partner,
            message,
            email_subject=self.env._("Installation approved - schedule your appointment"),
            email_body=self.env._(
                "Your installation quotation has been approved. Choose a suitable "
                "installation appointment at %(url)s.",
                url=portal_url,
            ),
        )

    def _notify_survey_confirmed(self, partner, notifier):
        portal_url = f"{notifier._get_base_url()}/my/orders/{self.id}"
        if self.company_id.visit_confirmation_policy == "payment":
            message = self.env._(
                "Payment received. Your site survey is confirmed. Amount: %(amount)s",
                amount=self._formatted_amount(self.amount_total),
            )
        else:
            message = self.env._(
                "Your site survey is confirmed after phone verification. Amount: %(amount)s",
                amount=self._formatted_amount(self.amount_total),
            )
        notifier.notify_customer(
            partner,
            message,
            email_template_xmlid="fieldservice_portal.email_visit_booked",
            email_values={"portal_url": portal_url},
        )

    def _notify_service_paid(self, partner, notifier):
        notifier.notify_customer(
            partner,
            self.env._(
                "Your service request and payment are confirmed. Amount: %(amount)s",
                amount=self._formatted_amount(self.amount_total),
            ),
        )

    def _get_portal_return_url(self):
        if self._is_installation_released():
            return f"/my/installation/{self.id}"
        parent = super()
        return parent._get_portal_return_url() if hasattr(parent, "_get_portal_return_url") else "/my/orders"
