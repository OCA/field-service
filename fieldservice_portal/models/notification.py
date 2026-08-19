import logging
from datetime import timedelta

from markupsafe import Markup, escape

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class FieldServiceNotification(models.AbstractModel):
    _name = "fieldservice.notification"
    _description = "Field Service Notification Helper"

    @api.model
    def _get_base_url(self):
        return self.env["ir.config_parameter"].sudo().get_param("web.base.url", "").rstrip("/")

    @api.model
    def _send_external_message(self, partner, message):
        return False

    @api.model
    def notify_customer(
        self,
        partner,
        customer_message,
        email_template_xmlid=None,
        email_values=None,
        email_subject=None,
        email_body=None,
    ):
        if not partner:
            return {"success": False, "error": "No partner provided"}

        results = {}
        if customer_message:
            try:
                external_result = self._send_external_message(partner, customer_message)
                if external_result:
                    results["external_message"] = external_result
            except Exception as exc:
                _logger.exception(
                    "External notification failed for res.partner %s: %s",
                    partner.id,
                    exc,
                )
                results["external_message"] = {"success": False, "error": str(exc)}

        if partner.email and (email_template_xmlid or (email_subject and email_body)):
            try:
                template = self.env.ref(
                    email_template_xmlid, raise_if_not_found=False
                ) if email_template_xmlid else False
                if email_template_xmlid and template:
                    context = {"default_email_to": partner.email}
                    if email_values:
                        context.update(email_values)
                    template.with_context(**context).send_mail(
                        partner.id,
                        force_send=True,
                        email_layout_xmlid="mail.mail_notification_light",
                    )
                    results["email"] = {"success": True}
                elif email_template_xmlid:
                    results["email"] = {"success": False, "error": "Template not found"}
                else:
                    self.env["mail.mail"].sudo().create(
                        {
                            "subject": email_subject,
                            "body_html": Markup("<p>%s</p>") % escape(email_body),
                            "email_to": partner.email_formatted or partner.email,
                            "email_from": (
                                self.env.company.email_formatted
                                or self.env.user.email_formatted
                            ),
                        }
                    ).send()
                    results["email"] = {"success": True}
            except Exception as exc:
                _logger.exception(
                    "Email notification failed for res.partner %s: %s",
                    partner.id,
                    exc,
                )
                results["email"] = {"success": False, "error": str(exc)}

        return results

    @api.model
    def _get_available_slots_text(self, route_type, limit=5):
        today = fields.Date.context_today(self)
        dayroutes = self.env["fsm.route.dayroute"].sudo().search(
            [
                ("date", ">=", today),
                ("date", "<=", today + timedelta(weeks=4)),
                ("order_remaining", ">", 0),
                ("route_id.route_type", "=", route_type),
                ("team_id.company_id", "=", self.env.company.id),
            ],
            order="date asc",
            limit=limit,
        )
        return "\n".join(
            self.env._(
                "%(date)s - %(route)s",
                date=dayroute.date,
                route=dayroute.route_id.name or "",
            )
            for dayroute in dayroutes
        )
