import logging

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class FsmOrderSurveySubmit(models.TransientModel):
    _name = "fsm.order.survey.submit"
    _description = "Submit Survey for FSM Order"

    fsm_order_id = fields.Many2one(
        "fsm.order",
        default=lambda self: self.env.context.get("active_id"),
        string="Survey Field Service Order",
    )
    fsm_order_person_id = fields.Many2one(
        related="fsm_order_id.person_id", string="Survey Person"
    )
    subject = fields.Char(
        "Subject", compute="_compute_subject", store=True, readonly=False
    )
    body = fields.Html(
        "Contents",
        sanitize_style=True,
        compute="_compute_body",
        store=True,
        readonly=False,
    )
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "fsm_order_survey_mail_compose_message_ir_attachments_rel",
        "wizard_id",
        "attachment_id",
        string="Attachments",
    )
    template_id = fields.Many2one(
        "mail.template",
        "Use template",
        index=True,
        domain="[('model', '=', 'fsm.order.survey.submit')]",
        default=lambda self: self.env.ref(
            "fieldservice_survey.mail_template_fsm_order_survey_submit",
            raise_if_not_found=False,
        ),
    )
    email_from = fields.Char(
        "From",
        required=True,
        default=lambda self: self.env.user.email_formatted,
        help="Email address of the sender",
    )
    author_id = fields.Many2one(
        "res.partner",
        string="Author",
        required=True,
        default=lambda self: self.env.user.partner_id.id,
        help="Author of the message.",
    )
    survey_template_id = fields.Many2one("survey.survey")
    recipient_ids = fields.Many2many(
        "res.partner",
        compute="_compute_recipients",
        store=True,
        readonly=False,
        string="Recipients",
    )
    deadline = fields.Date(
        string="Answer Deadline",
        required=True,
        default=lambda self: fields.Date.today() + relativedelta(months=1),
    )

    def _get_default_deadline(self):
        """Compute default deadline date."""
        return fields.Date.today() + relativedelta(months=1)

    @api.model
    def default_get(self, fields_list):
        """Override default_get to add custom defaults."""
        if not self.env.user.email:
            raise UserError(
                _(
                    "Unable to post message, please configure the sender's email address."
                )
            )
        result = super().default_get(fields_list)
        fsm_order_id = self.env.context.get("active_id") or result.get("fsm_order_id")
        fsm_order = self.env["fsm.order"].browse(fsm_order_id)
        if (
            "survey_template_id" in fields_list
            and fsm_order
            and not result.get("survey_template_id")
        ):
            result[
                "survey_template_id"
            ] = fsm_order.company_id.fsm_order_survey_template_id.id
        return result

    @api.depends("fsm_order_id")
    def _compute_recipients(self):
        """Compute the recipients of the survey."""
        for wizard in self.filtered(lambda w: w.fsm_order_id):
            wizard.recipient_ids = wizard.fsm_order_id.location_id.partner_id

    @api.depends("template_id")
    def _compute_subject(self):
        """Compute the subject for the email."""
        for wizard in self.filtered(lambda w: w.template_id):
            wizard.subject = wizard.template_id.subject

    @api.depends("template_id")
    def _compute_body(self):
        """Compute the body of the email."""
        for wizard in self.filtered(lambda w: w.template_id):
            wizard.body = wizard.template_id.body_html

    def _prepare_survey_answers(self, recipients):
        """Prepare survey answers."""
        answers = self.env["survey.user_input"]
        existing_answers = self.env["survey.user_input"].search(
            [
                ("survey_id", "=", self.survey_template_id.id),
                ("fsm_order_id", "=", self.fsm_order_id.id),
                ("partner_id", "in", recipients.ids),
            ]
        )
        partners_done = existing_answers.mapped("partner_id")
        for partner_done in partners_done:
            answers |= next(
                existing_answer
                for existing_answer in existing_answers.sorted(
                    lambda answer: answer.create_date, reverse=True
                )
                if existing_answer.partner_id == partner_done
            )

        for new_partner in recipients - partners_done:
            answers |= self.survey_template_id.sudo()._create_answer(
                partner=new_partner, check_attempts=False, deadline=self.deadline
            )
        return answers

    def _send_mail(self, answer):
        """Create mail specific for recipient containing notably its access token."""
        ctx = {"fsm_order_name": self.fsm_order_id.name}
        RenderMixin = self.env["mail.render.mixin"].with_context(**ctx)
        subject = RenderMixin._render_template(
            self.subject, "survey.user_input", answer.ids, post_process=True
        )[answer.id]
        body = RenderMixin._render_template(
            self.body, "survey.user_input", answer.ids, post_process=True
        )[answer.id]

        mail_values = {
            "email_from": self.email_from,
            "author_id": self.author_id.id,
            "model": None,
            "res_id": None,
            "subject": subject,
            "body_html": body,
            "attachment_ids": [(4, att.id) for att in self.attachment_ids],
            "auto_delete": True,
        }

        if answer.partner_id:
            mail_values["recipient_ids"] = [(4, answer.partner_id.id)]
        else:
            mail_values["email_to"] = answer.email

        try:
            template = self.env.ref(
                "mail.mail_notification_light", raise_if_not_found=True
            )
        except ValueError:
            _logger.warning(
                "QWeb template mail.mail_notification_light not found "
                "when sending survey mails. Sending without layouting."
            )
        else:
            template_ctx = {
                "message": self.env["mail.message"]
                .sudo()
                .new(
                    dict(
                        body=mail_values["body_html"],
                        record_name=self.survey_template_id.title,
                    )
                ),
                "model_description": self.env["ir.model"]
                ._get("fsm.order.survey.submit")
                .display_name,
                "company": self.env.company,
            }
            body = template._render(
                template_ctx, engine="ir.qweb", minimal_qcontext=True
            )
            mail_values["body_html"] = self.env[
                "mail.render.mixin"
            ]._replace_local_links(body)

        return self.env["mail.mail"].sudo().create(mail_values)

    def action_send(self):
        """Action for sending the survey email."""
        self.ensure_one()
        recipients = self.recipient_ids
        answers = self._prepare_survey_answers(recipients)
        answers.sudo().write(
            {
                "fsm_order_id": self.fsm_order_id.id,
                "fsm_order_person_id": self.fsm_order_person_id.id,
            }
        )
        for answer in answers:
            self._send_mail(answer)

        for person in self.recipient_ids.filtered(lambda e: e.user_id):
            answer = answers.filtered(
                lambda l: l.partner_id == person.user_id.partner_id
            )
            self.fsm_order_id.with_context(
                mail_activity_quick_update=True
            ).activity_schedule(
                "mail.mail_activity_data_todo",
                self.deadline,
                summary=_("Fill the answer form on survey"),
                note=_(
                    "An survey was requested. Please take time to fill "
                    'the <a href="%s" target="_blank">survey</a>'
                )
                % answer.get_start_url(),
                user_id=person.user_id.id,
            )

        self.fsm_order_id.partner_submitted_answer_survey_ids |= self.recipient_ids
        return {"type": "ir.actions.act_window_close"}
