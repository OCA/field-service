# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service Google Marker Icon Picker",
    "summary": "This module displays google marker icon picker based on"
    " apply widget on field",
    "license": "AGPL-3",
    "version": "14.0.1.1.0",
    "category": "Field Service",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": [
        "fieldservice_google_map",
        "web_widget_google_marker_icon_picker",
    ],
    "data": [
        "views/fsm_stage.xml",
    ],
    "development_status": "Beta",
    "external_dependencies": {"python": ["webcolors"]},
    "maintainers": [
        "wolfhall",
        "max3903",
    ],
    "installable": True,
    "auto_install": True,
}
