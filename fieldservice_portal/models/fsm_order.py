import logging

from odoo import models

_logger = logging.getLogger(__name__)


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    def write(self, vals):
        result = super().write(vals)
        if "stage_id" in vals:
            for order in self:
                try:
                    order._on_stage_change(vals["stage_id"])
                except Exception:
                    _logger.exception(
                        "Customer notification failed for fsm.order %s", order.id
                    )
        return result

    def _on_stage_change(self, new_stage_id):
        self.ensure_one()
        stage = self.env["fsm.stage"].sudo().browse(new_stage_id)
        partner = self._get_notification_partner()
        if not stage.exists() or not partner:
            return

        notifier = self.env["fieldservice.notification"]
        if stage.notification_event == "started":
            self._notify_started(partner, notifier)
        elif stage.notification_event == "completed":
            self._notify_completed(partner, notifier)

    def _get_notification_partner(self):
        self.ensure_one()
        if self.location_id.owner_id:
            return self.location_id.owner_id
        return self.partner_id or self.env["res.partner"]

    def _get_service_type(self):
        self.ensure_one()
        if self.type and self.type.service_type != "other":
            return self.type.service_type
        template = self.sale_id.sale_order_template_id
        return template.service_type if template else "other"

    def _notify_started(self, partner, notifier):
        self.ensure_one()
        person_name = self.person_id.name if self.person_id else self.env._("Technician")
        message = self.env._(
            "%(person)s is on the way.\nWork order: %(order)s",
            person=person_name,
            order=self.name or "",
        )
        notifier.notify_customer(partner, message)

    def _notify_completed(self, partner, notifier):
        self.ensure_one()
        service_type = self._get_service_type()
        if service_type == "survey":
            self._notify_survey_complete(partner, notifier)
        elif service_type == "installation":
            self._notify_installation_complete(partner, notifier)
        elif service_type in ("maintenance", "repair"):
            self._notify_service_complete(partner, notifier)
        else:
            notifier.notify_customer(partner, self.env._("The work has been completed."))

    def _notify_survey_complete(self, partner, notifier):
        notifier.notify_customer(
            partner,
            self.env._("The site survey is complete. Your quotation will follow shortly."),
            email_template_xmlid="fieldservice_portal.email_inspection_completed",
            email_values={"portal_url": f"{notifier._get_base_url()}/my/orders"},
        )

    def _notify_installation_complete(self, partner, notifier):
        notifier.notify_customer(
            partner,
            self.env._(
                "Installation is complete. The installed equipment is ready for use.\n"
                "Future service requests: %(url)s/my/requests",
                url=notifier._get_base_url(),
            ),
            email_template_xmlid="fieldservice_portal.email_installation_completed",
            email_values={"portal_url": f"{notifier._get_base_url()}/my/requests"},
        )

    def _notify_service_complete(self, partner, notifier):
        notifier.notify_customer(
            partner,
            self.env._("The service is complete and the installed equipment is operational."),
            email_template_xmlid="fieldservice_portal.email_maintenance_completed",
            email_values={"portal_url": f"{notifier._get_base_url()}/my/requests"},
        )
