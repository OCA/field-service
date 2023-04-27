# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Field Service Partner Relations",
    "summary": "Manage relations between contacts, companies and locations",
    "version": "14.0.1.0.0",
    "category": "Field Service",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "complexity": "normal",
    "license": "AGPL-3",
    "depends": ["partner_multi_relation", "fieldservice"],
    "data": ["views/fsm_location.xml", "views/menu.xml"],
    "demo": [
        "data/demo.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["max3903"],
}
