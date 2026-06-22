# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Field Service Vehicles",
    "summary": "Manage Field Service vehicles and assign drivers",
    "version": "17.0.1.1.0",
    "category": "Field Service",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": ["fieldservice"],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "views/fsm_vehicle.xml",
        "views/fsm_person.xml",
        "views/fsm_order.xml",
        "views/menu.xml",
    ],
    "license": "AGPL-3",
    "development_status": "Beta",
    "maintainers": ["wolfhall", "max3903"],
}
