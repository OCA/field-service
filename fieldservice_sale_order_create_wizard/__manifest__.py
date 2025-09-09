# Copyright 2025 Bernat Obrador (APSL-Nagarro)<bobrador@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Sale Order Create Wizard",
    "version": "15.0.1.1.0",
    "summary": "Create Sale Order from Field Service Kanban View",
    "category": "Field Service",
    "website": "https://github.com/OCA/field-service",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["BernatObrador"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "fieldservice_sale_stock_route",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/fsm_create_so_wizard.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "fieldservice_sale_order_create_wizard/static/src/js/*.js",
        ],
        "web.assets_qweb": [
            "fieldservice_sale_order_create_wizard/static/src/xml/*.xml",
        ],
    },
}
