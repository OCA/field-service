# Copyright (C) 2024 Open Source Integrators (<https://www.graymatterlogic.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Field Service - Expenses",
    "summary": "Report expenses from Field Service orders",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "category": "Field Service",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": ["fieldservice", "hr_expense"],
    "data": [
        "views/hr_expense_views.xml",
        "views/fsm_order_views.xml",
    ],
    "development_status": "Alpha",
    "maintainers": ["max3903"],
    "installable": True,
}
