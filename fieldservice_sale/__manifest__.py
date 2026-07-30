# Copyright (C) 2018 Gray Matter Logic
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Field Service - Sales",
    "version": "19.0.1.0.0",
    "summary": "Sell field services.",
    "category": "Field Service",
    "author": "Gray Matter Logic, Odoo Community Association (OCA)",
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
        "max3903",
        "brian10048",
    ],
    "installable": True,
}
