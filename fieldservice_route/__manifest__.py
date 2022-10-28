# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent consulting Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Field Service Route",
    "summary": "Organize the routes of each day.",
    "version": "15.0.1.0.0",
    "category": "Field Service",
    "license": "AGPL-3",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": ["fieldservice"],
    "data": [
        "data/ir_sequence.xml",
        "data/fsm_route_day_data.xml",
        "data/fsm_stage_data.xml",
        "security/ir.model.access.csv",
        "views/fsm_route_day.xml",
        "views/fsm_route.xml",
        "views/fsm_location.xml",
        "views/fsm_route_dayroute.xml",
        "views/fsm_order.xml",
        "views/menu.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["max3903"],
}
