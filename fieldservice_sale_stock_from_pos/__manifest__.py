# Copyright (C) 2025 Bernat Obrador (APSL - Nagarro) bobrador@apsl.net
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Sale Stock From POS",
    "version": "17.0.1.0.0",
    "summary": "Create Field Service Orders from POS Orders",
    "category": "Field Service",
    "author": "APSL- Nagarro, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": [
        "fieldservice",
        "fieldservice_sale_stock",
        "point_of_sale",
        "pos_order_to_sale_order",
    ],
    "data": [
        "views/res_config_settings.xml",
    ],
    "license": "AGPL-3",
    "maintainers": [
        "borbrador",
    ],
    "assets": {
        "web.assets_tests": [
            "fieldservice_sale_stock_from_pos/static/tests/tours/**/*",
        ],
    },
    "installable": True,
}
