# Copyright (C) 2021 - TODAY, Gray Matter Logic
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Purchase",
    "summary": "Manage FSM purchases and link purchase orders to field service orders",
    "author": "Gray Matter Logic, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "category": "Field Service",
    "license": "AGPL-3",
    "version": "19.0.1.0.0",
    "depends": [
        "fieldservice",
        "purchase",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/fsm_person.xml",
        "views/fsm_order.xml",
        "views/purchase_order.xml",
    ],
    "development_status": "Beta",
    "maintainers": [
        "max3903",
    ],
    "installable": True,
}
