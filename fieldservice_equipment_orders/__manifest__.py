# Copyright (C) 2022 Rafnix Guzman rafnixg
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Field Service Orders - Smart Button",
    "summary": "Add a smart stats button for fsm.orders and go to your FSM Orders view.",
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/field-service",
    "category": "Field Service",
    "author": "Odoo Community Association (OCA), Rafnixg",
    "depends": ["base", "portal", "website", "fieldservice_equipment_website"],
    "data": [
        "views/fieldservice_equipment_orders_views.xml",
    ],
    "demo": [],
}
