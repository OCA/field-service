# Copyright 2023 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, http
from odoo.exceptions import AccessDenied
from odoo.http import request
from odoo.osv import expression

from odoo.addons.survey.controllers.main import Survey

FSM_ORDER_ID = "fsm_order_id"
PARTNER_ID = "partner_id"
FSM_ORDER_PERSON_ID = "fsm_order_person_id"


class FsmOrderSurveySurvey(Survey):
    def _get_user_input_domain(self, survey, line_filter_domain, **post):
        user_input_domain = super()._get_user_input_domain(
            survey, line_filter_domain, **post
        )

        fsm_order_id = post.get(FSM_ORDER_ID)
        if not fsm_order_id:
            return user_input_domain

        try:
            fsm_order = request.env["fsm.order"].sudo().browse(int(fsm_order_id))
        except ValueError:
            raise AccessDenied(_("Invalid FSM Order ID"))

        user = request.env.user
        partner = user.partner_id
        person = request.env["fsm.person"].search([(PARTNER_ID, "=", partner.id)])

        if user.has_group("fieldservice_survey.group_fsm_survey_user"):
            return expression.AND(
                [[("fsm_order_id", "=", fsm_order.id)], user_input_domain]
            )

        if partner.id in fsm_order.partner_submitted_answer_survey_ids.ids:
            return expression.AND(
                [
                    [FSM_ORDER_ID, "=", fsm_order.id],
                    [FSM_ORDER_PERSON_ID, "=", person.id],
                ],
                user_input_domain,
            )

        raise AccessDenied(_("You do not have access to this FSM Order Survey"))

    @http.route(
        "/fsm_order/<int:fsm_order_id>/results", type="http", auth="user", website=True
    )
    def survey_results(self, fsm_order_id, **post):
        try:
            fsm_order = request.env["fsm.order"].sudo().browse(fsm_order_id)
        except ValueError:
            raise AccessDenied(_("Invalid FSM Order ID"))

        if (
            fsm_order.person_id.partner_id == request.env.user.partner_id
            and not request.env.user.has_group(
                "fieldservice_survey.group_fsm_survey_user"
            )
        ):

            return request.render(
                "http_routing.http_error",
                {
                    "status_code": "Forbidden",
                    "status_message": "You don't have access to this survey "
                    "related to your FSM Order.",
                },
            )

        user = request.env.user
        partner = user.partner_id
        person = request.env["fsm.person"].search([(PARTNER_ID, "=", partner.id)])
        survey_sudo = None
        answer = None

        if user.has_group(
            "fieldservice_survey.group_fsm_survey_user"
        ) or user.has_group("base.group_system"):
            survey_sudo = (
                request.env["survey.user_input"]
                .sudo()
                .search([(FSM_ORDER_ID, "=", fsm_order.id)], limit=1)
                .survey_id
            )

        if partner.id in fsm_order.partner_submitted_answer_survey_ids.ids:
            answer = (
                request.env["survey.user_input"]
                .sudo()
                .search(
                    [
                        (FSM_ORDER_ID, "=", fsm_order.id),
                        (FSM_ORDER_PERSON_ID, "=", person.id),
                    ],
                    limit=1,
                )
            )

        if answer:
            survey_sudo = answer.survey_id

        if not survey_sudo:
            raise AccessDenied(_("No survey found for the given FSM Order"))

        post["fsm_order_id"] = fsm_order_id
        user_input_lines_sudo, search_filters = self._extract_filters_data(
            survey_sudo, post
        )
        survey_data = survey_sudo._prepare_statistics(user_input_lines_sudo)
        question_and_page_data = survey_sudo.question_and_page_ids._prepare_statistics(
            user_input_lines_sudo
        )

        template_values = {
            "survey": survey_sudo,
            "question_and_page_data": question_and_page_data,
            "survey_data": survey_data,
            "search_filters": search_filters,
            "search_finished": "true",
            "fsm_order_id": fsm_order_id,
        }

        return request.render("survey.survey_page_statistics", template_values)
