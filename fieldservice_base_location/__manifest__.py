# Copyright (C) 2025 Bernat Obrador (APSL - Nagarro)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Field Service - Base location",
    "summary": "Autocomplete address in field service locations",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "category": "Field Service",
    "author": "Apsl - Nagarro, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": ["fieldservice", "base_location"],
    "data": [
        "views/fsm_location.xml",
    ],
    "auto_install": True,
    "maintainers": ["BernatObrador"],
}
