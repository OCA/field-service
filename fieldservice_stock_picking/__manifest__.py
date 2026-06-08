# Copyright (C) 2026 Innovyou
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Stock Picking",
    "summary": "Send out and receive materials through Field Service Orders "
    "using standard stock transfers",
    "version": "16.0.1.0.0",
    "category": "Field Service",
    "author": "Innovyou, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": ["fieldservice_stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/fsm_template.xml",
        "views/fsm_order.xml",
    ],
    "license": "AGPL-3",
    "development_status": "Beta",
    "maintainers": ["eLBati"],
}
