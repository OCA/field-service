# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Fieldservice Website Sale",
    "version": "15.0.1.0.1",
    "summary": "This module links e-commerce orders with field service, ",
    "automating delivery scheduling and FSM order assignment."
    "category": "Field Service",
    "website": "https://github.com/OCA/field-service",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["ppyczko"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "fieldservice_availability",
        "fieldservice_sale_stock_route",
        "website_sale",
    ],
    "data": ["views/calendar_templates.xml", "views/res_config_settings_views.xml"],
    "assets": {
        "web.assets_frontend": [
            "fieldservice_website_sale/static/src/js/payment_form.js",
            "fieldservice_website_sale/static/src/js/fsm_calendar.js",
            "fieldservice_website_sale/static/src/scss/fsm_calendar.scss",
        ],
    },
}
