# Copyright (C) 2026 Gray Matter Logic
# Copyright (C) 2019 Serpent consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service Route",
    "summary": "Organize the routes of each day.",
    "version": "19.0.1.0.0",
    "category": "Field Service",
    "license": "AGPL-3",
    "author": "Gray Matter Logic, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": ["fieldservice"],
    "data": [
        "data/ir_sequence.xml",
        "data/fsm_route_day_data.xml",
        "data/fsm_stage_data.xml",
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
        "views/fsm_route_day.xml",
        "views/fsm_route.xml",
        "views/fsm_location.xml",
        "views/fsm_route_dayroute.xml",
        "views/fsm_order.xml",
        "views/menu.xml",
    ],
    "demo": [
        "demo/fsm_route.xml",
        "demo/fsm_location.xml",
        "demo/fsm_route_dayroute.xml",
        "demo/fsm_order.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["max3903"],
}
