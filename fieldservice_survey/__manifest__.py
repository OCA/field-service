# Copyright 2023 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Fieldservice Survey",
    "summary": """
        This module enable integration the fieldservice app with survey""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": [
        "fieldservice",
        "survey",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings.xml",
        "views/survey_survey.xml",
        "views/survey_user_input.xml",
        "views/fsm_order.xml",
        "views/survey_templates_statistics.xml",
        "data/fsm_order_survey_data.xml",
        "data/mail_data.xml",
        "wizard/fsm_order_survey_submit.xml",
    ],
}
