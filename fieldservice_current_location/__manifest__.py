# Copyright (C) 2025, APSL - Nagarro Bernat Obrador Mesquida
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Current Location",
    "version": "17.0.1.0.0",
    "summary": "Use current location on fsm orders",
    "category": "Field Service",
    "author": "APSL - Nagarro, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": ["fieldservice", "base_geolocalize"],
    "external_dependencies": {"python": ["geopy"]},
    "data": ["views/fsm_order.xml", "security/ir.model.access.csv"],
    "assets": {
        "web.assets_backend": [
            "fieldservice_current_location/static/src/js/geolocate_button.esm.js",
            "fieldservice_current_location/static/src/xml/geolocate_button.xml",
        ],
    },
    "license": "AGPL-3",
    "maintainers": ["BernatObrador", "peluko00"],
    "installable": True,
}
