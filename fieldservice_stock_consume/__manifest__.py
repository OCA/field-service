# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Field Service - Consume Parts from Stock",
    "summary": "Technicians request parts from stock on a field service order",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/field-service",
    "category": "Field Service",
    "author": "Pop Solutions, Odoo Community Association (OCA)",
    "maintainers": ["marcos-mendez"],
    "depends": ["fieldservice_stock"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/fsm_stock_consume_views.xml",
        "views/fsm_order_views.xml",
    ],
}
