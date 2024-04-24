# Copyright 2023 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestFsmOrder(TransactionCase):
    def setUp(self):
        super(TestFsmOrder, self).setUp()
        self.test_loc_partner = self.env["res.partner"].create(
            {"name": "Test Loc Partner", "phone": "ABC", "email": "tlp@email.com"}
        )
        self.test_location = self.env["fsm.location"].create(
            {
                "name": "Test Location",
                "phone": "123",
                "email": "tp@email.com",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
            }
        )
        self.fsm_order = self.env["fsm.order"].create(
            {
                "location_id": self.test_location.id,
                "date_start": datetime.today(),
                "date_end": datetime.today() + timedelta(hours=2),
                "request_early": datetime.today(),
            }
        )
        self.survey_template = self.env.ref(
            "fieldservice_survey.customer_satisfaction_survey"
        )
        self.template = self.env.ref(
            "fieldservice_survey.mail_template_fsm_order_survey_submit"
        )
        self.survey_submit_wizard = self.env["fsm.order.survey.submit"].create(
            {
                "fsm_order_id": self.fsm_order.id,
                "fsm_order_person_id": self.fsm_order.person_id.id,
                "email_from": "test@example.com",
                "author_id": self.test_loc_partner.id,
                "template_id": self.template.id,
                "survey_template_id": self.survey_template.id,
                "recipient_ids": [(6, 0, [self.fsm_order.location_id.partner_id.id])],
                "deadline": fields.Date.today() + relativedelta(months=1),
            }
        )

    def test_get_default_deadline(self):
        default_deadline = self.survey_submit_wizard._get_default_deadline()
        expected_deadline = fields.Date.today() + relativedelta(months=1)
        self.assertEqual(default_deadline, expected_deadline)

    def test_default_get(self):
        fields_list = ["survey_template_id"]
        self.env.context = {"active_id": self.fsm_order.id}
        self.survey_submit_wizard.env.user.email = "test@example.com"
        result = self.survey_submit_wizard.default_get(fields_list)
        expected_survey_template_id = (
            self.fsm_order.company_id.fsm_order_survey_template_id.id
        )
        self.assertEqual(result.get("survey_template_id"), expected_survey_template_id)

    def test_compute_recipients(self):
        self.survey_submit_wizard._compute_recipients()
        expected_recipients = (
            self.survey_submit_wizard.fsm_order_id.location_id.partner_id
        )
        self.assertEqual(self.survey_submit_wizard.recipient_ids, expected_recipients)

    def test_compute_subject(self):
        self.survey_submit_wizard._compute_subject()
        expected_subject = self.template.subject
        self.assertEqual(self.survey_submit_wizard.subject, expected_subject)

    def test_prepare_survey_answers(self):
        recipients = self.survey_submit_wizard.recipient_ids
        existing_answers = self.env["survey.user_input"].search(
            [
                ("survey_id", "=", self.survey_submit_wizard.survey_template_id.id),
                ("fsm_order_id", "=", self.survey_submit_wizard.fsm_order_id.id),
                ("partner_id", "in", recipients.ids),
            ]
        )
        partners_done = existing_answers.mapped("partner_id")
        answers = self.survey_submit_wizard._prepare_survey_answers(recipients)

        missing_answers = recipients - partners_done

        self.assertTrue(
            all(
                any(answer.partner_id == new_partner for answer in answers)
                for new_partner in missing_answers
            ),
            "Survey answer not created for partner",
        )

        self.assertTrue(
            all(
                any(answer.partner_id == partner_done for answer in answers)
                for partner_done in partners_done
            ),
            "Existing survey answer not included for partner",
        )

    def test_send_mail(self):
        self.maxDiff = None
        answer = self.env["survey.user_input"].create(
            {
                "survey_id": self.survey_template.id,
                "email": "recipient@example.com",
                "partner_id": self.test_loc_partner.id,
            }
        )
        ctx = {"fsm_order_name": self.fsm_order.name}
        RenderMixin = self.env["mail.render.mixin"].with_context(**ctx)
        subject = RenderMixin._render_template(
            self.survey_submit_wizard.subject,
            "survey.user_input",
            answer.ids,
            post_process=True,
        )[answer.id]

        self.env.ref("mail.mail_notification_light")
        mail = self.survey_submit_wizard._send_mail(answer)
        self.env.ref("mail.mail_notification_light").unlink()

        self.assertTrue(mail)
        self.assertEqual(mail.email_from, self.survey_submit_wizard.email_from)
        self.assertEqual(mail.author_id.id, self.survey_submit_wizard.author_id.id)
        self.assertEqual(mail.subject, subject)
        self.assertEqual(mail.attachment_ids, self.survey_submit_wizard.attachment_ids)
        self.assertEqual(mail.recipient_ids.ids, [answer.partner_id.id])

    def test_send_mail_no_partner(self):
        self.maxDiff = None

        answer = self.env["survey.user_input"].create(
            {
                "survey_id": self.survey_template.id,
                "email": "recipient@example.com",
            }
        )
        ctx = {"fsm_order_name": self.fsm_order.name}
        RenderMixin = self.env["mail.render.mixin"].with_context(**ctx)
        subject = RenderMixin._render_template(
            self.survey_submit_wizard.subject,
            "survey.user_input",
            answer.ids,
            post_process=True,
        )[answer.id]
        mail = self.survey_submit_wizard._send_mail(answer)

        self.assertTrue(mail)
        self.assertEqual(mail.email_from, self.survey_submit_wizard.email_from)
        self.assertEqual(mail.author_id.id, self.survey_submit_wizard.author_id.id)
        self.assertEqual(mail.subject, subject)
        self.assertEqual(mail.attachment_ids, self.survey_submit_wizard.attachment_ids)
        self.assertEqual(mail.email_to, answer.email)

    def test_action_send(self):
        recipients = self.survey_submit_wizard.recipient_ids
        answers = self.survey_submit_wizard._prepare_survey_answers(recipients)

        self.survey_submit_wizard._send_mail(answers)
        self.survey_submit_wizard.fsm_order_id = self.fsm_order

        result = self.survey_submit_wizard.action_send()

        self.assertTrue(result["type"], "ir.actions.act_window_close")
        self.assertEqual(
            self.fsm_order.partner_submitted_answer_survey_ids,
            self.survey_submit_wizard.recipient_ids,
        )
        self.assertEqual(len(answers), len(self.survey_submit_wizard.recipient_ids))
