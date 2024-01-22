# Copyright 2023 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    def _get_default_fsm_order_survey_template_id(self):
        return self.env.ref(
            "fieldservice_survey.fsm_order_survey_submit_template",
            raise_if_not_found=False,
        )

    fsm_order_survey_template_id = fields.Many2one("survey.survey")
