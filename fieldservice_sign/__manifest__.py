# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Sign",
    "summary": "Customer signature capture and document signing on FSM orders",
    "version": "19.0.1.0.0",
    "category": "Field Service",
    "author": "Gray Matter Logic, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "license": "AGPL-3",
    "depends": ["fieldservice", "sign_oca"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/fsm_order_views.xml",
        "views/sign_oca_request_views.xml",
        "report/fsm_order_report_templates.xml",
    ],
    "demo": [
        "demo/sign_oca_role.xml",
        "demo/sign_oca_template.xml",
        "demo/sign_oca_template_item.xml",
        "demo/res_company.xml",
        "demo/fsm_order.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["max3903"],
    "installable": True,
}
