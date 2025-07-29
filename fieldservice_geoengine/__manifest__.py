# Copyright (C) 2018 - TODAY, Open Source Integrators
# Copyright (C) 2023 - TODAY Pytech SRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service Geoengine",
    "summary": "Display Field Service locations on a map with Open Street Map",
    "license": "AGPL-3",
    "version": "17.0.1.2.0",
    "category": "Field Service",
    "author": "Open Source Integrators, Odoo Community Association (OCA), Pytech SRL",
    "website": "https://github.com/OCA/field-service",
    "depends": ["base_geoengine", "fieldservice"],
    "data": [
        "security/res_groups.xml",
        "views/fsm_location.xml",
        "views/fsm_team.xml",
        "views/fsm_order.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "fieldservice_geoengine/static/src/js/**",
        ]
    },
    "development_status": "Beta",
    "maintainers": ["wolfhall", "max3903"],
}
