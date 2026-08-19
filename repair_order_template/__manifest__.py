# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Repair Order Template",
    "summary": "Use templates to save time when creating repair orders",
    "version": "19.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["ivantodorovich"],
    "website": "https://github.com/OCA/repair",
    "license": "AGPL-3",
    "category": "Repair",
    "depends": ["repair"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/repair_order_template.xml",
        "views/repair_order.xml",
    ],
    "demo": [
        "demo/repair_order_template.xml",
    ],
}
