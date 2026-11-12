# Copyright (C) 2018 - TODAY, Open Source Integrators
# Copyright (C) 2023 - TODAY Pytech SRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service Geoengine",
    "summary": "Display Field Service locations on a map with Open Street Map",
    "license": "AGPL-3",
    "version": "19.0.1.0.0",
    "category": "Field Service",
    "author": "Gray Matter Logic, Odoo Community Association (OCA), Pytech SRL",
    "website": "https://github.com/OCA/field-service",
    "depends": ["base_geoengine", "fieldservice", "fieldservice_route", "mail"],
    "data": [
        "security/res_groups.xml",
        "views/fsm_location.xml",
        "views/fsm_team.xml",
        "views/fsm_order.xml",
        "views/fsm_person.xml",
        "views/fsm_route.xml",
        "views/fsm_route_dayroute.xml",
    ],
    "demo": [
        "demo/fsm_person_geoloc.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "fieldservice_geoengine/static/src/js/**",
        ]
    },
    "development_status": "Beta",
    "maintainers": ["wolfhall", "max3903"],
}
