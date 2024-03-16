# Copyright 2023 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    fsm_order_survey_template_id = fields.Many2one(
        "survey.survey",
        related="company_id.fsm_order_survey_template_id",
        readonly=False,
    )

    module_fieldservice_survey = fields.Boolean(string="Field Service Survey")
