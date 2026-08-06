# Copyright (C) 2022 Rafnix Guzman
# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Field Service - Equipment Location History",
    "summary": "Track and execute equipment transfers between stock locations",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/field-service",
    "category": "Field Service",
    "author": "Pop Solutions, Odoo Community Association (OCA)",
    "maintainers": ["marcos-mendez"],
    "depends": ["fieldservice_equipment_stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/fsm_equipment_location_history_views.xml",
        "views/fsm_equipment_views.xml",
    ],
}
