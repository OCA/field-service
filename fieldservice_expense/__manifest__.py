# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Field Service - Expenses",
    "summary": "Manage expenses of orders",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "category": "TMS",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": ["fieldservice", "hr_expense", "fieldservice_account"],
    "data": [
        "views/hr_expense_views.xml",
        "views/fsm_order_views.xml",
    ],
    "demo": [],
    "development_status": "Alpha",
    "maintainers": ["max3903", "EdgarRetes"],
}
