# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service Web Timeline",
    "summary": "This module is a display timeline view of the Field Service"
    " order in Odoo.",
    "version": "17.0.1.0.0",
    "category": "Field Service",
    "license": "AGPL-3",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": ["fieldservice", "web_timeline"],
    "data": ["views/fsm_order.xml", "views/fsm_team.xml"],
    "development_status": "Beta",
    "maintainers": ["wolfhall", "max3903"],
    "uninstall_hook": "uninstall_hook",
}
