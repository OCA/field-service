# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Field Service - Sales",
    "version": "16.0.1.1.0",
    "summary": "Sell field services.",
    "category": "Field Service",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": [
        "fieldservice",
        "sale_management",
        "fieldservice_account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/res_groups.xml",
        "views/fsm_location.xml",
        "views/fsm_order.xml",
        "views/product_template.xml",
        "views/sale_order.xml",
    ],
    "license": "AGPL-3",
    "development_status": "Beta",
    "maintainers": [
        "wolfhall",
        "max3903",
        "brian10048",
    ],
    "installable": True,
}
