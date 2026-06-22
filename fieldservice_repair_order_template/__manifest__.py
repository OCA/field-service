# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Repair Order Template",
    "summary": "Use Repair Order Templates when creating a repair orders",
    "version": "17.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["ivantodorovich"],
    "website": "https://github.com/OCA/field-service",
    "license": "AGPL-3",
    "category": "Field Service",
    "depends": [
        "fieldservice_repair",
        "repair_order_template",
    ],
    "data": [
        "views/fsm_template.xml",
    ],
}
