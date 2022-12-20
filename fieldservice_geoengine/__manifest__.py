# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service Geoengine",
    "summary": "Display Field Service locations on a map with Open Street Map",
    "license": "AGPL-3",
    "version": "14.0.1.0.0",
    "category": "Field Service",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": ["base_geoengine", "fieldservice"],
    "data": ["security/res_groups.xml", "views/fsm_team.xml", "views/fsm_order.xml"],
    "development_status": "Beta",
    "maintainers": ["wolfhall", "max3903"],
}
