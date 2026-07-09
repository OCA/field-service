# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Field Service - Mobile",
    "summary": "Field Service Mobile Backend Support.",
    "license": "AGPL-3",
    "version": "19.0.1.0.0",
    "category": "Field Service",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": [
        "fieldservice_stage_server_action",
        "stock",
        "analytic",
        "maintenance",
        "fieldservice_vehicle",
        "fieldservice_sale",
        "calendar",
        "payment",
    ],
    "data": [
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
        "security/fieldservice_mobile_security.xml",
        "data/server_actions.xml",
        "data/base_automation.xml",
        "data/feature_line.xml",
        "data/feature_mapping.xml",
        "views/res_config_settings.xml",
        "views/fsm_stage_view.xml",
        "views/fsm_order_view.xml",
        "views/mobile_feature_mapping.xml",
        "views/mobile_feature_line.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["wolfhall", "max3903"],
}
