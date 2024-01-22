# Copyright 2023 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SurveySurvey(models.Model):

    _inherit = "survey.survey"

    is_fsm_order_survey = fields.Boolean(
        string="FSM Order Survey Managers Only",
        help="Check this option to restrict the answers to survey managers only.",
    )
