# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Field Service - Purchase",
    "summary": "Manage purchase requests in orders",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "category": "FSM",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": ["purchase", "fieldservice_account"],
    "data": [
        "views/fsm_order.xml",
        "views/purchase_order_views.xml",
    ],
    "demo": [],
    "development_status": "Alpha",
    "maintainers": ["max3903", "EdgarRetes"],
}
