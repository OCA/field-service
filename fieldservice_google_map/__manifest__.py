# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service Google Map",
    "summary": "Display map views on Field Service orders and locations",
    "license": "AGPL-3",
    "version": "19.0.1.0.1",
    "category": "Field Service",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": [
        "fieldservice",
        "web_view_google_map",
    ],
    "data": [
        "views/fsm_order.xml",
        "views/fsm_location.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "fieldservice_google_map/static/src/views/google_map/google_map_api_key_prompt.esm.js",
            "fieldservice_google_map/static/src/views/google_map/google_map_api_key_prompt.xml",
            "fieldservice_google_map/static/src/views/google_map/google_map_api_key_prompt.scss",
        ],
    },
    "installable": True,
    "development_status": "Beta",
    "maintainers": [
        "wolfhall",
        "max3903",
    ],
}
