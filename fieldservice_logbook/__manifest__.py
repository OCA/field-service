# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service Equipment Logbook",
    "summary": "Manage Field Service equipment logbooks",
    "version": "15.0.1.0.0",
    "category": "Field Service",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": ["fieldservice"],
    "data": [
        "security/ir.model.access.csv",
        "security/res_groups.xml",
        "views/fsm_equipment_logbook.xml",
        "views/fsm_equipment.xml",
        "views/fsm_order.xml",
        "views/fsm_location.xml",
    ],
    "license": "AGPL-3",
    "development_status": "Beta",
    "maintainers": ["yankinmax"],
}
